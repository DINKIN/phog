from PIL import Image
from PIL.ExifTags import TAGS
from iptcinfo import IPTCInfo


"""
maxSize method by Andrius Miasnikovas
http://andrius.miasnikovas.lt/2010/04/creating-thumbnails-from-photos-with-python-pil/
"""
def maxSize(image, maxSize, thumbnail, method = 3):
    exif=get_exif(image)
    orientation=exif.get('Orientation',None)

    if orientation!=None:
        if orientation == 1:
            # Nothing
            image = image.copy()
        elif orientation == 2:
            # Vertical Mirror
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotation 180
            image = image.transpose(Image.ROTATE_180)
        elif orientation == 4:
            # Horizontal Mirror
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            # Horizontal Mirror + Rotation 270
            image = image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation == 6:
            # Rotation 270
            image = image.transpose(Image.ROTATE_270)
        elif orientation == 7:
            # Vertical Mirror + Rotation 270
            image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 8:
            # Rotation 90
            image = image.transpose(Image.ROTATE_90)

    imAspect = float(image.size[0])/float(image.size[1])
    outAspect = float(maxSize[0])/float(maxSize[1])
 
    if thumbnail:
        width=maxSize[0]
        height=int(float(maxSize[0])/float(image.size[0])*float(image.size[1]))
        inter_image=image.resize((width, height), method)
        offset=int(float(height-maxSize[1])/4.0)
        return inter_image.crop((0,offset,width,offset+maxSize[1]))
    elif imAspect >= outAspect:
        return image.resize((maxSize[0], int((float(maxSize[0])/imAspect) + 0.5)), method)
    else:
        return image.resize((int((float(maxSize[1])*imAspect) + 0.5), maxSize[1]), method)
 

def resizeAndSave(imgpath,size,destpath,thumbnail=False):
    img = Image.open(imgpath)
    newimg = maxSize(img,size,thumbnail,Image.BILINEAR)
    newimg.save(destpath) 
    return newimg.size

def get_exif(i):
    ret = {}
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def getTitle(filepath,filename):
    # try to get the ITPC title (from Lightroom), fall back to image filename
    filename=filename[0:filename.lower().find(".jpg")]
    try:
        info=IPTCInfo(filepath)
        return info.data.get(5,filename)
    except:
        return filename
