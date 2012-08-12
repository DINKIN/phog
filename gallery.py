import os
import imageprocessing
import math
from jinja2 import Environment, FileSystemLoader

RESERVED_TEMPLATES=['base.html','index.html','albumpage.html','viewimage.html']

class Gallery:


	def __init__(self,config,root_path):
		self.config=config
		self.source_image_path=os.path.join(root_path,"source_images")
		self.theme_name=config.get("gallery","theme")
		self.themes_path = os.path.join(root_path,"themes")
		self.theme_path=os.path.join(self.themes_path,self.theme_name)

		if not os.path.exists(self.theme_path):
			raise Exception("theme '%s' not found "%self.theme_name)

		self.templates_path = os.path.join(self.theme_path,"templates")

		self.template_path=os.path.join(root_path,"templates")
		self.output_path=os.path.join(root_path,"output")

		self.small_size=self.config.get("gallery","small_size").split(",")
		self.large_size=self.config.get("gallery","large_size").split(",")

		self.configureTemplates()
		self.discoverPlugins()

	def discoverPlugins(self):
		pass

	def configureTemplates(self):
		self.tempEnv = Environment(loader=FileSystemLoader(self.templates_path))

	def getTemplate(self,templateName):
		return self.tempEnv.get_template(templateName)

	def generate(self):

		images=self.discoverImages()
		# plugin call point - pre thumbnail generation, post file discovery (to add additional files)

		print "generating image sizes:"
		#self.generateImages(images)

		# plugin call point - pre page generation, with images as arguments (to provide extra context for pages)
		print "generating pages"
		self.generatePages(images)
	
		self.copyStaticContent()

		# plugin call point, generation complete - passed images and pages (to tweak generated content)

	def copyStaticContent(self):
		pass

	def discoverImages(self):
		images=[]
		for filename in os.listdir(self.source_image_path):
			if filename.find(".jpg")!=-1:
				images.append({'path':os.path.join(self.source_image_path,filename),'filename':filename})

		print "%s images found"%len(images)
		return images

	def generatePages(self,images):
		indexIsAlbumPage = self.config.getboolean("gallery","INDEX_IS_ALBUM_PAGE")
		imagesPerPage = int(self.config.get("gallery","IMAGES_PER_PAGE"))

		pages=int(math.ceil((len(images)/float(imagesPerPage))))

		print "%s gallery pages"%pages

		page_context={
			'images_per_page':imagesPerPage,
			'pages':pages,
			'imagecount':len(images),
			'gallerytitle':self.config.get("gallery","title"),
		}

		if indexIsAlbumPage:
			currPageName="index.html"
			
		else:
			currPageName="page1.html"

		# generate image pages
		


		pagelinks=[]
		for page in range(pages):
			pagelinks.append({'title':(int(page)+1),'link':"page%s.html"%(int(page)+1)})
		page_context['pagelinks']=pagelinks

		# generate album pages
		for page in range(pages):
			pageno=page+1
			print "generating page %s"%pageno
			page_images=images[page*imagesPerPage:pageno*imagesPerPage]
			page_context['images']=page_images
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
		indexIsAlbumPage = self.config.getboolean("gallery","INDEX_IS_ALBUM_PAGE")
		
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
		for imgdetails in images:
			imgpath,imgname=imgdetails['path'],imgdetails['filename']

			imgtitle = imageprocessing.getTitle(imgpath,imgname)
			imgdetails['title']=imgtitle
			print "image title is %s"%imgtitle
			print "processing %s"%imgpath
			output_path=os.path.join(self.output_path,"small_%s"%imgname)
			imgdetails['small']=output_path
			print "generating small size"
			imageprocessing.resizeAndSave(imgpath,(int(self.small_size[0]),int(self.small_size[1])),output_path)

			output_path=os.path.join(self.output_path,"large_%s"%imgname)
			imgdetails['large']=output_path
			print "generating large size"
			imageprocessing.resizeAndSave(imgpath,(int(self.large_size[0]),int(self.large_size[1])),output_path)
			


