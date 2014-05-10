from PIL import Image
foo = Image.open("/opt/photoboard/uploads/275ba001-7eb5-4a87-b9b5-7e31eb7cd992.JPG")
newsize = tuple([i/10 for i in foo.size])

print foo.size
exit()
# I downsize the image with an ANTIALIAS filter (gives the highest quality)
new = foo.resize(newsize,Image.ANTIALIAS)
# The saved downsized image size is 24.8kb
new.save("/opt/photoboard/uploads/275ba001-7eb5-4a87-b9b5-7e31eb7cd992.JPG",optimize=True,quality=95)
print new.size
# The saved downsized image size is 22.9kb
