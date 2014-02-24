
class MailChimpPlugin:

    def notify(self, config, output_path):
        print "notifying via mailchimp"


def getPlugin():
    return MailChimpPlugin()
