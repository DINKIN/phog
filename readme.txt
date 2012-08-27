Phog
====

What is phog?
-------------
A static-site generator along the lines of Jekyll, Volt, nanoc etc. but for the purpose of generating image & video galleries and photo blogs.  It's not a general purpose blogging engine - galleries are the main focus.  I see photo blogs as another type of gallery.

I have tried self-hosting galleries before (e.g menalto gallery) but found the hosting to be a hassle (patching apache, php, mysql, gallery itself), so I then moved on to photo hosting services.  I wanted a good degree of control over the presentation of my images and I also wanted particular features because I'm mainly sharing photos with family - e.g password protected galleries, email notification, comments without sign-up.  I found everything I needed in Posterous but then Posterous was taken over by Twitter and it's future doesn't look good now.  I started shopping around for other options but worry about the same thing happening again and the desire to have complete control over my images and how they appear started me thinking my own solution.

I wanted something that gives complete flexibility and control over my galleries, but that uses 'cloud' storage solutions to eliminate the hassle of hosting.   I had been playing with some site generators like Jekyll and so was inspired to create something similar for photo galleries and photo blogs.


Features
--------

* Multi-threaded image thumbnail generation
* Title extraction through ITPC
* Orientation detection through EXIF
* Video transcoding, screencap grabbing via ffmpeg
* Jinja2 template-based theming
* Static html galleries, Ajax galleries or photo blogs
* Responsive default ajax theme based on customised Galleria, modified to support Facebook comments and flowplayer
* Extensible through plugins
* Amazon S3 upload plugin included
* 



