import yaml
import sys, os

def setDefaults():

    c = {'raspberryPiConfig':
         {'ADCtoCobbler':{
             'SPICLK':18,
             'SPIMISO':23,
             'SPIMOSI': 24,
             'SPICS': 25
             },
          'debug':0,
          'adcPortWithFSR':0,
          'tolerance':16,
          'maxChange':-410,
          'getMoarBeansNow':300,
          'alertChannels':[''],
          'checkTime': 2,
          'plotlyCredsFile':'./plotlyCreds.sec',
          'updateTime:': 86400,
          'updateChannels':['']
         },
         'emailConfiguration':
         {'smtpServer':'localhost',
          'gmailCredsFile':'',
          'fromAddr':'',
          'toAddr':'',
          'emailAlertMessage': 'This is your friendly BeanBot letting you know that it looks like you are low on beans.\n\nAccording to the bean weight sensor, you have {0}% of beans left.\n\nIt is {1} and I hope you have time to get more beans soon.\n\nHappy coffeeing!',
          'emailAlertSubject': 'Low Bean Alert!',
          'emailUpdateSubject': 'Coffee Bean Status',
          'emailUpdateMessage': 'According to your weight sensor, you have {0}% of beans left.\n\nHello, this is your friendly BeanBot updating you on your coffee bean status.  You have {0}% left, so there is no alert at this time, but I will let you know if you get low (based on your configured options).\nHappy coffeeing!'
         },
         'twitterConfiguration':
         {'twitterCredsFile': './twitterCreds.sec',
          'twitterAlertHashtags': ['caen', 'beanbot', 'coffebeans',
                                   'buymoarcoffeebeans', 'coffeeemergency'],
          'twitterAlertMessage': 'OH NOES! The bean inventory dangerously low! ({0}% at {1})',
          'twitterUpdateHashtags': ['caen', 'beanbot', 'coffebeans'],
          'twitterUpdateMessage': 'The bean inventory is {0}% at {1}.'
      }
     }

    return (c)

def readConfig (file):

    try:
        f = open(file)
    except:
        errorString = '''I couldn't open the file {0} to read the settings, so I'll use the defaults. (Logged from {1}/{2})
        '''.format(file,os.path.abspath(os.path.dirname(sys.argv[0])),sys.argv[0])
        logging.warning(errorString)
        exit (1)

    # this is list() to make the load_all generator generate
    # everything and put it into config before the file is close()'d
    configDocs = list(yaml.safe_load_all(f))
    f.close()

    # why safe_load_all makes an array is beyond me; I must be missing
    # something, because it makes the order of the YAML file matter,
    # and that's no good

    config = setDefaults()

    for doc in configDocs:
        config[doc['name']] = doc

    return(config)


if __name__ == "__main__":

    import pprint as pp
    import logging

    configFile = './scaleConfig.yaml1'

    cfg = readConfig(configFile)

    if cfg['raspberryPiConfig']['debug']:
        logging.basicConfig(level=logging.DEBUG)

    logging.warning("The debug setting is %s",cfg['raspberryPiConfig']['debug'])

    logging.debug("And everything else is:")

    logging.debug(pp.pformat(cfg))

    if 'plotly' in cfg['raspberryPiConfig']['alertChannels']:
        logging.debug("Alert: Plot.ly")
    else:
        logging.debug("Alert: no Plot.ly")
