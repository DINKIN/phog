import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key


class S3PublishPlugin:

    def upload(self, config, output_path):
        print "uploading to S3"

        conn = S3Connection(
            config.get("S3", "S3_ACCESS_KEY"),
            config.get("S3", "S3_SECRET_KEY"))

        root_bucket = conn.get_bucket(config.get("S3", "S3_ROOT_BUCKET_NAME"))

        subdirectory = config.get("S3", "S3_SUBDIRECTORY")

        existing_content = root_bucket.list(prefix=subdirectory)

        for key in existing_content:
            print "deleting %s" % key.key
            key.delete()

        for root, dirs, files in os.walk(output_path):
            rel_path = os.path.relpath(root, output_path)
            if rel_path == ".":
                rel_path = ""
            else:
                rel_path += "/"

            for file in files:
                s3_filename = subdirectory + "/" + rel_path + file
                print "uploading %s" % s3_filename
                key = Key(root_bucket)
                key.key = s3_filename
                key.set_contents_from_filename(os.path.join(root, file))
                key.set_acl('public-read')


def getPlugin():
    return S3PublishPlugin()
