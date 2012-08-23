import os
import imageprocessing
import videoprocessing
import math
import shutil
import hashlib
from jinja2 import Environment, FileSystemLoader
from multiprocessing import Pool, Queue
from plugins import PluginManager
import uuid

RESERVED_TEMPLATES=['base.html','index.html','albumpage.html','viewimage.html','viewvideo.html']

def processImage(config):
	fileName,output_path,small_size,large_size,password_hash=config
	print "processing %s"%fileName
	imgpath,imgname=os.path.split(fileName)
	returnmap={}
	imgtitle = imageprocessing.getTitle(fileName,imgname)
	returnmap['title']=imgtitle
	returnmap['filename']=imgname
			
	img_output_path=os.path.join(output_path,"small_%s"%imgname)
	returnmap['small']=img_output_path
	real_img_output_path=os.path.join(output_path,"%ssmall_%s"%(password_hash,imgname))
			
	returnmap['smallsize']=imageprocessing.resizeAndSave(fileName,(int(small_size[0]),int(small_size[1])),real_img_output_path,thumbnail=True)

	img_output_path=os.path.join(output_path,"large_%s"%imgname)
	returnmap['large']=img_output_path
	real_img_output_path=os.path.join(output_path,"%slarge_%s"%(password_hash,imgname))
			
	returnmap['largesize']=imageprocessing.resizeAndSave(fileName,(int(large_size[0]),int(large_size[1])),real_img_output_path)
	return returnmap


class MediaObject:

	TYPE_PHOTO=0
	TYPE_VIDEO=1

	def __init__(self,type=TYPE_PHOTO,thumb_path=None,source_path="",filename=""):
		self.id=uuid.uuid4()
		self.type=type
		self.thumb_path=thumb_path
		self.filename=filename
		self.source_path=source_path


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

		imageFilenames=self.discoverImages()

		videos=self.discoverAndProcessVideos()

		print videos

		images=self.generateImages(imageFilenames)

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
				images.append(os.path.join(self.source_image_path,filename))

		print "%s images found"%len(images)
		return images

	def discoverAndProcessVideos(self):
		transcoded_videos=[]
		raw_videos=[]
		for filename in os.listdir(self.source_video_path):
			extension=filename.lower()[-3:]
			if extension in ['m4v','mp4']:
				transcoded_videos.append(filename)
			elif extension in ['avi','mov','mvi','wmv']:
				raw_videos.append(filename)

		print "found raw videos, to be transcoded: %s"%raw_videos
		print "found already transcoded videos: %s"%transcoded_videos

		vp = videoprocessing.VideoProcessor()

		completed_video_paths=[]

		# copy the already-transcoded videos to the output directory
		for filename in transcoded_videos:
			source_path=os.path.join(self.source_video_path,filename)
			target_path=os.path.join(self.output_path,filename)

			print "copying m4v video: %s"%source_path
			shutil.copy(source_path,target_path)
			completed_video_paths.append(target_path)

		# transcode the others
		for filename in raw_videos:
			source_path=os.path.join(self.source_video_path,filename)
			target_path=os.path.join(self.output_path,filename[:filename.find(".")]+".m4v")

			print "transcoding %s to %s"%(source_path,target_path)
			params=vp.getSizeAndDuration(source_path)
			vp.trancodeRawVideo(source_path,target_path,params,self.video_size)
			completed_video_paths.append(target_path)


		completed_videos=[]
		for video_path in completed_video_paths:
			# generate thumbnail
			thumb_name=vp.getScreencap(video_path)

			# get dimensions and duration
			params=vp.getSizeAndDuration(video_path)
			params['filename']=thumb_name
			params['type']='video'
			params['video_name']=os.path.split(video_path)[1]
			completed_videos.append(params)

		return completed_videos



	def generatePages(self, images, videos, extra_context):
		indexIsAlbumPage = self.config.getboolean("theme","INDEX_IS_ALBUM_PAGE")
		imagesPerPage = int(self.config.get("theme","IMAGES_PER_PAGE"))

		# merge video and photo records
		media=[]
		for img in images:
			currPageName="view_photo_%s.html"%img['id']
			img['page_name']=currPageName

			media.append(img)

		vidid=0
		for vid in videos:
			pageName="view_video_%s.html"%vidid
			vid['id']=vidid
			vid['page_name']=pageName
			media.append(vid)
			vidid+=1

		# set up previous and next links
		for i in range(len(media)):
			prevlink=None
			nextlink=None
			if i>0:
				prevlink=media[i-1]['page_name']
			if i<(len(media)-1):
				nextlink=media[i+1]['page_name']
			media[i]['next_link']=nextlink
			media[i]['prev_link']=prevlink


		# generate image pages
		for img in images:
			page_context={
				'img':img,
				'root_url':self.config.get("gallery","ROOT_URL"),
			}
			self.renderPage("viewimage.html",img['page_name'],page_context)

		# generate video pages
		for video_details in videos:
			self.renderPage("viewvideo.html",video_details['page_name'],video_details)


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


	def generateImages(self, imageFilenames):
		p = Pool()

		password_protected=self.config.getboolean("gallery","password_protected")
		if password_protected:
			password_hash=hashlib.sha512(self.config.get("gallery","password")).hexdigest()
			print "password hash is %s"%password_hash
		else:
			password_hash=""


		images=p.map(processImage,[[fn,self.output_path,self.small_size,self.large_size,password_hash] for fn in imageFilenames])

		id=0
		for img in images:
			img['id']=id
			img['type']='image'
			id+=1

		return images
			

