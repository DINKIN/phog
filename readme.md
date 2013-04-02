Phog
====

What is phog?
-------------
A static-site generator along the lines of Jekyll, Volt, nanoc etc. but for the purpose of generating image & video galleries and photo blogs.  It's not a general purpose blogging engine - galleries are the main focus.  A photo blog is a gallery template in phog.

I have tried self-hosting galleries before (e.g menalto gallery) but found the hosting to be a hassle (patching apache, php, mysql, gallery itself), so I then moved on to photo hosting services.  I wanted a good degree of control over the presentation of my images and I also wanted particular features because I'm mainly sharing photos with family - e.g password protected galleries, email notification, comments without sign-up.  I found everything I needed in Posterous but then Posterous was taken over by Twitter and it's now being shut down.  I started shopping around for other options but worry about the same thing happening again and the desire to have complete control over my images and how they appear started me thinking my own solution.

I wanted something that gives complete flexibility and control over my galleries, but that uses 'cloud' storage solutions to eliminate the hassle of hosting.   I had been playing with some site generators like Jekyll and so was inspired to create something similar for photo galleries and photo blogs.

Status
------
Phog should be considered 'beta'.  I use it for my own galleries but it's a new project, so it needs some battle testing.  It could also do with some more themes and plugins, so feel free to contribute some! I'm planning an email notification plugin to inform people (e.g family) when a new gallery is posted.  I also started working on a password protection system but it needs some more work.



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


Usage
-----

phog create

Create a gallery project directory, which looks like this:

    output
    plugins
    source_images
    source_video
    themes
    config.txt

phog gen

Scan the source photo and video directories, generate image sizes, transcode video, generate gallery pages and other static pages.

phog upload

Run any configured upload plugins (S3 enabled by default)

Configuration
-------------

Once you have created a gallery

        [gallery]
        TITLE=
        ROOT_URL=

        SMALL_IMAGE_SIZE=500,500
        LARGE_IMAGE_SIZE=1000,1000

        VIDEO_MAX_SIZE=640,480

        UPLOAD_FULL_SIZE=True

        THEME=default




Plugins
-------

Events:

prePageGeneration

upload

notify

Sample Galleries
----------------

staticgallery

ajaxgallery




