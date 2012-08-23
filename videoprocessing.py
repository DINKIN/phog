import os
import sys
import subprocess
import re
import math
import shutil
from qtfaststart import processor


class VideoProcessor:

	def __init__(self):
		pass

	def getFFMpeg(self):
		return self.which("ffmpeg")
		

	def getScreencap(self,video_path):
		path,filename=os.path.split(video_path)
		capfilename=filename[:filename.find(".")]+".jpg"
		cap_path=os.path.join(path,capfilename)
		capargs=[self.getFFMpeg(),"-y","-itsoffset","-4","-i",video_path,"-vcodec","mjpeg","-vframes","1","-an","-f","rawvideo","-s","320x240",cap_path]

		process = subprocess.Popen(capargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stderr = process.communicate()

		return capfilename


	def trancodeRawVideo(self,source_path,target_path,video_params,video_target_size):
		sourceAspect=float(video_params['width'])/float(video_params['height'])
		targetAspect=float(video_target_size[0])/float(video_target_size[1])

		if sourceAspect>targetAspect:
			output_width=video_target_size[0]
			output_height=(float(video_target_size[0])/float(video_params['width']))*float(video_params['height'])
		else:
			output_height=video_target_size[1]
			output_width=(float(video_target_size[1])/float(video_params['height']))*float(video_params['width'])

		output_width=int(math.floor(float(output_width)/2.0)*2.0)
		output_height=int(math.floor(float(output_height)/2.0)*2.0)

		# 1 = clockwise 90, 2 = counter clockwise 90
		# if filename contains r90 then transpose=1
		# if filename contains r270 then transpose=2
		extraargs=[]
		if source_path.find("r90")!=-1:
			extraargs=["-vf","transpose=1"]
		elif source_path.find("r270")!=-1:
			extraargs=["-vf","transpose=2"]


		print output_width,output_height
		print "aspects:",sourceAspect,targetAspect

		path,filename=os.path.split(target_path)
		tmpfile=os.path.join(path,"tmp_%s"%filename)
		transcodeArgs=[self.getFFMpeg(),"-y","-i",source_path,"-s","%sx%s"%(output_width,output_height),"-r","25","-b","2M","-bt","4M","-acodec","libfaac","-ar","44100","-ab","96k","-vcodec","libx264","-preset","medium","-sameq"]
		transcodeArgs.extend(extraargs)
		transcodeArgs.append(tmpfile)
		
		process = subprocess.Popen(transcodeArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
		    out = process.stdout.read(1)
		    if out == '' and process.poll() != None:
		        break
		    if out != '':
		        sys.stdout.write(out)
		        sys.stdout.flush()

		processor.process(tmpfile,target_path)
		os.remove(tmpfile)

		

	def getSizeAndDuration(self,filename):
		ffmpegPath=self.getFFMpeg()
		process = subprocess.Popen([ffmpegPath,  '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stderr = process.communicate()

		matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()
 	
 		matches.update(re.search(r"Video:.* (?P<width>\d+)x(?P<height>\d+)",stdout,re.DOTALL).groupdict())

 		print matches
 		return matches


	"""
	thanks to Jay on Stackoverflow for this:
	"""
	def which(self,program):
	    import os
	    def is_exe(fpath):
	        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

	    fpath, fname = os.path.split(program)
	    if fpath:
	        if is_exe(program):
	            return program
	    else:
	        for path in os.environ["PATH"].split(os.pathsep):
	            exe_file = os.path.join(path, program)
	            if is_exe(exe_file):
	                return exe_file

	    return None


if __name__=="__main__":
	filename=sys.argv[1]
	print "testing with filename %s"%filename

	vp = VideoProcessor()
	print vp.getSizeAndDuration(filename)
	print vp.trancodeRawVideo(filename)
	print vp.getScreencap(filename)
