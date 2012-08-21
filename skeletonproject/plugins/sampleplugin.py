
class SamplePlugin:


	def prePageGeneration(self,config,source_image_path,source_video_path,images,videos):
		print "sample plugin: pre page generation"
		return {'sampletext':'hello world'}

	def upload(self,config,output_path):
		print "sample plugin: upload"

	def notify(self,config,output_path):
		print "sample plugin: notify"


def getPlugin():
	return SamplePlugin()