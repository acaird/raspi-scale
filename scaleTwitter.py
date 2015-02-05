import yaml
import sys, os

def tweetStatus(aToken, aSecret, cToken, cSecret, tweet):

    if (len(tweet)>140):
        print >> sys.stderr, "Tweet is longer than 140 characters, can't send"
        return(0)

    import twitter

    api=twitter.Api(consumer_key=cToken,
                    consumer_secret=cSecret,
                    access_token_key=aToken,
                    access_token_secret=aSecret)

    status = api.PostUpdate(tweet)


if __name__ == "__main__":
    twitterCredsFile = './twitterCreds.sec'

    try:
        f = open(twitterCredsFile)
    except:
        print "=========================== ERROR ==========================="
        print "I couldn't open the file '{0}'".format(emailConfigFile)
        print "to read the twitter credentials, so I can't tweet and"
        print "am giving up."
        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
        print "=========================== ERROR ==========================="
        exit (1)

    twitterCredentials = yaml.safe_load(f)
    f.close()

    tweetStatus(twitterCredentials['accessToken'],
                twitterCredentials['accessSecret'],
                twitterCredentials['consumerKey'],
                twitterCredentials['consumerSec'],
                'y u no have beans? #testtweet #coffebeans')
