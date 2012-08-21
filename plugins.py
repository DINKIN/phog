import os
import imp

class PluginManager:

	def __init__(self):
		self.plugins=[]

	def discoverPlugins(self,path):
		for file in os.listdir(path):
			if file[-3:]=='.py':
				mod = imp.load_source(file[:-3],os.path.join(path,file))
				self.plugins.append(mod.getPlugin())

	def prePageGeneration(self,config,source_image_path,source_video_path,images,videos):
		extra_context={}
		for plugin in self.plugins:
			if hasattr(plugin,'prePageGeneration'):
				extra_context.update(plugin.prePageGeneration(config,source_image_path,source_video_path,images,videos))

		return extra_context

	def upload(self,config,output_path):
		for plugin in self.plugins:
			if hasattr(plugin,'upload'):
				plugin.upload(config,output_path)

	def notify(self,config,output_path):
		for plugin in self.plugins:
			if hasattr(plugin,'notify'):
				plugin.notify(config,output_path)

	