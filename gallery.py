import os
import imageprocessing
import videoprocessing
import math
import shutil
import hashlib
import ConfigParser
from jinja2 import Environment, FileSystemLoader
from multiprocessing import Pool, Queue
from plugins import PluginManager
import uuid

RESERVED_TEMPLATES=['base.html','index.html','albumpage.html','viewimage.html','viewvideo.html','embedvideo.html']

def processImage(config):
    image=config[0]

    imgpath,imgname=image.source_path,image.filename
    imgtitle = imageprocessing.getTitle(image.filename,imgname)
    image.title=imgtitle

    img_output_path=os.path.join(image.output_path,"small_%s"%imgname)
    image.small_path=img_output_path
    image.thumb_filename="small_%s"%imgname
            
    image.small_size=imageprocessing.resizeAndSave(image.source_path,(int(image.target_small_size[0]),int(image.target_small_size[1])),img_output_path,thumbnail=True)

    img_output_path=os.path.join(image.output_path,"large_%s"%imgname)
    image.large_path=img_output_path
    image.large_filename="large_%s"%imgname
            
    image.large_size=imageprocessing.resizeAndSave(image.source_path,(int(image.target_large_size[0]),int(image.target_large_size[1])),img_output_path)
    return image


class MediaObject:

    TYPE_PHOTO=0
    TYPE_VIDEO=1

    def __init__(self,type=TYPE_PHOTO,thumb_path=None,source_path="",filename="",thumb_filename="",output_path=""):
        self.id=uuid.uuid4()
        self.type=type
        self.thumb_path=thumb_path
        self.filename=filename
        self.source_path=source_path
        self.output_path=output_path
        self.thumb_filename=thumb_filename

        if type==MediaObject.TYPE_VIDEO:
            extension=filename.lower()[-3:]
            self.transcoded=(extension in ['m4v','mp4'])

    def __repr__(self):
        if self.type==MediaObject.TYPE_PHOTO:
            return "Photo - %s"%self.filename
        elif self.type==MediaObject.TYPE_VIDEO:
            return "Video - %s, pre-transcoded: %s"%(self.filename,self.transcoded)


class Gallery:


    def __init__(self,config,root_path):
        self.config=config
        self.root_path=root_path
        self.source_image_path=os.path.join(root_path,"source_images")
        self.source_video_path=os.path.join(root_path,"source_videos")
        self.theme_name=config.get("gallery","theme")
        self.themes_path = os.path.join(root_path,"themes")
        self.theme_path=os.path.join(self.themes_path,self.theme_name)

        if not os.path.exists(self.theme_path):
            raise Exception("theme '%s' not found "%self.theme_name)
        
        themeconfigpath=os.path.join(self.theme_path,"config.txt")

        if not os.path.exists(themeconfigpath):
            raise Exception("couldn't find theme config.txt")

        self.config.read(themeconfigpath)
        
        self.templates_path = os.path.join(self.theme_path,"templates")

        self.template_path=os.path.join(root_path,"templates")
        self.output_path=os.path.join(root_path,"output")

        self.small_size=self.config.get("gallery","small_image_size").split(",")
        self.large_size=self.config.get("gallery","large_image_size").split(",")

        self.video_size=self.config.get("gallery","video_max_size").split(",")

        self.configureTemplates()
        self.discoverPlugins()

    def discoverPlugins(self):
        self.pluginManager=PluginManager()
        self.pluginManager.discoverPlugins(os.path.join(self.root_path,"plugins"))

    def configureTemplates(self):
        self.tempEnv = Environment(loader=FileSystemLoader(self.templates_path))

    def getTemplate(self,templateName):
        return self.tempEnv.get_template(templateName)

    def generate(self):

        images=self.discoverImages()

        videos=self.discoverAndProcessVideos()

        print videos

        images=self.generateImages(images)

        # plugin call point - pre page generation, with images as arguments (to provide extra context for pages)
        extra_context=self.pluginManager.prePageGeneration(self.config,self.source_image_path,self.source_video_path,images,videos)

        self.generatePages(images,videos,extra_context)
    
        self.copyStaticContent()


    def upload(self):
        # plugin call point, generation complete - upload
        self.pluginManager.upload(self.config,self.output_path)

        # plugin call point, generation complete - notify
        self.pluginManager.notify(self.config,self.output_path)

    def copyStaticContent(self):
        static_path=os.path.join(self.theme_path,"static")
        static_output_path=os.path.join(self.output_path,"static")
        if os.path.exists(static_output_path):
            shutil.rmtree(static_output_path)
        shutil.copytree(static_path,static_output_path)

    def discoverImages(self):
        images=[]
        for filename in os.listdir(self.source_image_path):
            if filename.lower().find(".jpg")!=-1:
                image=MediaObject(source_path=os.path.join(self.source_image_path,filename),filename=filename,output_path=self.output_path)
                image.target_small_size=self.small_size
                image.target_large_size=self.large_size
                images.append(image)

        print "%s images found"%len(images)
        return images

    def discoverAndProcessVideos(self):
        videos=[]
        vp = videoprocessing.VideoProcessor()

        for filename in os.listdir(self.source_video_path):
            video=MediaObject(type=MediaObject.TYPE_VIDEO,
                filename=filename,
                source_path=os.path.join(self.source_video_path,filename),
                output_path=self.output_path)

            videos.append(video)

            if video.transcoded:
                # copy already transcoded video
                target_path=os.path.join(self.output_path,video.filename)
                print "copying m4v video: %s"%video.source_path
                shutil.copy(video.source_path,target_path)
            else:
                # transcode the others
                target_filename=video.filename[:video.filename.find(".")]+".m4v"
                video.filename=target_filename
                target_path=os.path.join(self.output_path,target_filename)

                print "transcoding %s to %s"%(video.source_path,target_path)
                params=vp.getSizeAndDuration(video.source_path)
                vp.trancodeRawVideo(video.source_path,target_path,params,self.video_size)
            
            video.thumb_path=vp.getScreencap(video.source_path,self.output_path)
            video.thumb_filename=os.path.split(video.thumb_path)[1]

            # get dimensions and duration
            params=vp.getSizeAndDuration(os.path.join(self.output_path,video.filename))
            video.width=params.get('width',None)
            video.height=params.get('height',None)
            video.hours=params.get('hours',None)
            video.minutes=params.get('minutes',None)
            video.seconds=params.get('seconds',None)
            video.title=filename
            

        return videos



    def generatePages(self, images, videos, extra_context):
        try:
            themeMode = self.config.get("theme","THEME_MODE")
        except ConfigParser.NoOptionError:
            themeMode = 'static'

        # merge video and photo records
        media=[]
        media.extend(videos)
        media.extend(images)
        for mediaobject in media:
            if mediaobject.type==MediaObject.TYPE_PHOTO:
                mediaobject.page="view_photo_%s.html"%mediaobject.id
            elif mediaobject.type==MediaObject.TYPE_VIDEO:
                mediaobject.page="view_video_%s.html"%mediaobject.id

        if themeMode=='ajax':
            return self.generateAjaxPages(media,extra_context)
        elif themeMode=='static':
            return self.generatePlainPages(media,extra_context)
        else:
            raise Exception("unknown mode in theme")

    def generateAjaxPages(self, media, extra_context):

        page_context={
            'root_url':self.config.get("gallery","ROOT_URL"),
            'imagecount':len(media),
            'media':media,
            'gallerytitle':self.config.get("gallery","title"),
        }

        page_context.update(extra_context)

        self.renderPage("index.html","index.html",page_context)

        # create video embed pages
        for mediaitem in media:
            if mediaitem.type==MediaObject.TYPE_VIDEO:
                local_page_context={
                    'video':mediaitem,
                    'root_url':self.config.get("gallery","ROOT_URL"),
                }
                self.renderPage("embedvideo.html","embed_%s.html"%mediaitem.filename,local_page_context)

        self.renderStaticPages(page_context)


    def generatePlainPages(self, media, extra_context):
        indexIsAlbumPage = self.config.getboolean("theme","INDEX_IS_ALBUM_PAGE")
        imagesPerPage = int(self.config.get("theme","IMAGES_PER_PAGE"))


        # set up previous and next links
        for i in range(len(media)):
            prevlink=None
            nextlink=None
            if i>0:
                prevlink=media[i-1].page
            if i<(len(media)-1):
                nextlink=media[i+1].page
            media[i].next_link=nextlink
            media[i].prev_link=prevlink


        pages=int(math.ceil((len(media)/float(imagesPerPage))))

        page_context={
            'root_url':self.config.get("gallery","ROOT_URL"),
            'images_per_page':imagesPerPage,
            'pages':pages,
            'imagecount':len(media),
            'gallerytitle':self.config.get("gallery","title"),
        }

        page_context.update(extra_context)

        pagelinks=[]
        for page in range(pages):
            if page==0 and indexIsAlbumPage:
                pagelinks.append({'title':(int(page)+1),'link':"index.html"})
            else:
                pagelinks.append({'title':(int(page)+1),'link':"page%s.html"%(int(page)+1)})
        page_context['pagelinks']=pagelinks

        # generate album pages
        if indexIsAlbumPage:
            currPageName="index.html"
        else:
            currPageName="page1.html"
        for page in range(pages):
            pageno=page+1
            print "generating page %s"%pageno
            page_media=media[page*imagesPerPage:pageno*imagesPerPage]

            # set the owner page for the media items
            for mediaitem in page_media:
                mediaitem.home_page=currPageName

            page_context['media']=page_media
            page_context['pageno']=pageno

            prevlink=None
            if page>0:
                prevlink="page%s.html"%page
            nextlink=None
            if pageno<pages:
                nextlink="page%s.html"%(int(pageno)+1)

            page_context['prevlink']=prevlink
            page_context['nextlink']=nextlink

            self.renderPage("albumpage.html",currPageName,page_context)
            
            
            currPageName="page%s.html"%(pageno+1)


        # generate image and video view pages
        for mediaitem in media:
            if mediaitem.type==MediaObject.TYPE_PHOTO:
                local_page_context={
                    'img':mediaitem,
                    'root_url':self.config.get("gallery","ROOT_URL"),
                }
                self.renderPage("viewimage.html",mediaitem.page,local_page_context)

            if mediaitem.type==MediaObject.TYPE_VIDEO:
                local_page_context={
                    'video':mediaitem,
                    'root_url':self.config.get("gallery","ROOT_URL"),
                }
                self.renderPage("viewvideo.html",mediaitem.page,local_page_context)


        self.renderStaticPages(page_context)

    def renderStaticPages(self,context):
        indexIsAlbumPage = self.config.getboolean("theme","INDEX_IS_ALBUM_PAGE")
        
        if not indexIsAlbumPage:
            self.renderPage("index.html","index.html",context)

        # render any other template not in the list of reserved names
        for template in self.tempEnv.list_templates():
            if template not in RESERVED_TEMPLATES:
                print "rendering static page - %s"%template
                self.renderPage(template,template,context)

    def renderPage(self,templateName,outputName,context):
        page_template=self.getTemplate(templateName)
        
        html=page_template.render(context)
        outfile=open(os.path.join(self.output_path,outputName),"w")
        outfile.write(html)
        outfile.close()


    def generateImages(self, images):
        p = Pool()

        images=p.map(processImage,[[image] for image in images])

        print images

        return images
            

