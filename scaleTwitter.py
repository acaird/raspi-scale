import yaml
import sys, os

# pip install python-twitter, not pip install twitter

def tweetStatus(twitterCredsFile, tweet):

    if (len(tweet)>140):
        print >> sys.stderr, "Tweet is longer than 140 characters, can't send"
        return(0)

    import twitter

    try:
        f = open(twitterCredsFile)
        twitterCredentials = yaml.safe_load(f)
        f.close()
    except:
        print "=========================== ERROR ==========================="
        print "I couldn't open the file '{0}'".format(emailConfigFile)
        print "to read the twitter credentials, or maybe I couldn't log in, "
        print "so I can't tweet and am giving up."
        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
        print "=========================== ERROR ==========================="
        exit (1)


    api = twitter.Api(access_token_key=twitterCredentials['accessToken'],
                      access_token_secret=twitterCredentials['accessSecret'],
                      consumer_key=twitterCredentials['consumerKey'],
                      consumer_secret=twitterCredentials['consumerSec'])

    status = api.PostUpdate(tweet)


if __name__ == "__main__":

    import argparse
    import scaleConfig

    configFile = './scaleConfig.yaml'

    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", action="store", dest="configFile",
                        help="specify a configuration file")
    args = parser.parse_args()

    if args.configFile:
	configFile = args.configFile

    cfg = scaleConfig.readConfig(configFile)

    tweetStatus(cfg['twitterConfiguration']['twitterCredsFile'],
                'y u no have beans? #testtweet #coffebeans')
