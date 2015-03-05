import yaml
import sys, os

# pip install python-twitter, not pip install twitter

def tweetStatus(twitterCredsFile, tweet):

    if (len(tweet)>140):
        logging.error ("Tweet is longer than 140 characters, can't send")
        return(0)

    import twitter

    try:
        f = open(twitterCredsFile)
        twitterCredentials = yaml.safe_load(f)
        f.close()
    except:
        errorString = '''I couldn't open the file {0} to read the Twitter credentials, so I'm giving up (Logged from {1}/{2})
        '''.format(twitterCredsFile,os.path.abspath(os.path.dirname(sys.argv[0])),sys.argv[0])

        logging.error(errorString)

        exit (1)


    api = twitter.Api(access_token_key=twitterCredentials['accessToken'],
                      access_token_secret=twitterCredentials['accessSecret'],
                      consumer_key=twitterCredentials['consumerKey'],
                      consumer_secret=twitterCredentials['consumerSec'])

    status = api.PostUpdate(tweet)


if __name__ == "__main__":

    import argparse
    import scaleConfig
    import logging

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
