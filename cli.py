import argparse
import os
import sys
import shutil
import ConfigParser
import gallery


def create(args):
    project_name = vars(args)['name']
    print "creating skeleton project named '%s'" % project_name

    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        print "Project directory '%s' already exists" % project_path
        sys.exit(-1)

    skeletonpath = os.path.join(os.path.dirname(__file__), 'skeletonproject')

    shutil.copytree(skeletonpath, project_path)

    config_path = os.path.join(project_path, 'config.txt')

    config = ConfigParser.RawConfigParser()
    config.readfp(open(config_path))

    config.set('gallery', 'shortname', project_name)
    config.set('gallery', 'title', raw_input("Enter gallery title:"))

    config.write(open(config_path, "w"))

    print "%s project skeleton created." % project_name


def getGallery():
    config = ConfigParser.RawConfigParser()
    configpath = os.path.join(os.getcwd(), "config.txt")

    if not os.path.exists(configpath):
        print "couldn't find config.txt"

    configfile = open(configpath)

    config.readfp(configfile)

    gal = gallery.Gallery(config, os.getcwd())

    return gal


def gen(args):
    gal = getGallery()
    gal.generate()


def upload(args):
    gal = getGallery()
    gal.upload()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Phog Image Gallery Generator")
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser('create', help="create help")
    create_parser.add_argument('name', help="name of the project")
    create_parser.set_defaults(func=create)

    gen_parser = subparsers.add_parser('gen', help="gen help")
    gen_parser.set_defaults(func=gen)

    upload_parser = subparsers.add_parser('upload', help="upload help")
    upload_parser.set_defaults(func=upload)

    args = parser.parse_args()
    print "Phog - Static Gallery Generator"
    args.func(args)


if __name__ == "__main__":
    parse_args()
