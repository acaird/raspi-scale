
def processLowBeanAlerts (fsr, alertState, cfg, currentTime):

    beans = int((fsr/1024.)*100)

    # set the alertStates to 1 (alerted) and do the necessary
    # alerts if we seem to have too few beans
    if fsr < cfg['raspberryPiConfig']['getMoarBeansNow']:
        for alert in cfg['raspberryPiConfig']['alertChannels']:
            if alertState[alert] == 0:
                logging.debug ("%s Doing low bean alert %s",currentTime, alert)
                if alert == 'twitter':
                    hashTags = " ".join(["#"+m for m in cfg['twitterConfiguration']['twitterAlertHashtags']])
                    tweet   = cfg['twitterConfiguration']['twitterAlertMessage']+" "+ hashTags
                    tweet   = tweet.format(beans,currentTime)

                    scaleTwitter.tweetStatus(cfg['twitterConfiguration']['twitterCredsFile'],
                                             tweet)

                if alert == 'email':
                    subject = cfg['emailConfiguration']['emailAlertSubject']
                    body    = cfg['emailConfiguration']['emailAlertMessage'].format(beans,currentTime)

                    scaleEmail.sendEmail (cfg['emailConfiguration']['smtpServer'],
                                          cfg['emailConfiguration']['gmailCredsFile'],
                                          cfg['emailConfiguration']['fromAddr'],
                                          cfg['emailConfiguration']['toAddr'],
                                          subject, body)

                alertState[alert] = 1
        alertState.sync()

    # reset all of the alert channel states to 0 if we are 10%
    # above the bean limit and if we had previously set the alert
    # channel states
    if fsr > (cfg['raspberryPiConfig']['getMoarBeansNow'] * 1.1) and sum([alertState[m] for m in alertState]) > 0:
        logging.debug ("%s plenty of beans; resetting alerts",currentTime)
        for alert in alertState:
            alertState[alert] = 0
        alertState.sync()

if __name__ == "__main__":
    import yaml
    import shelve
    import scaleConfig
    import scaleTwitter
    import scaleEmail
    import argparse
    import datetime
    import logging

    configFile = './scaleConfig.yaml'

    parser = argparse.ArgumentParser()
    parser.add_argument ("-d", "--debug", type=int, choices=[0,1],
                         nargs='?', const=1,
                         help="turn debugging on (1) or off (0); this overrides"+
                         "the value in the configuration file ")
    parser.add_argument("-c","--config", action="store", dest="configFile",
                        help="specify a configuration file")
    parser.add_argument("-f","--fsr", action="store", dest="fsr", type=int,
                        help="specify a fake FSR value (default=230)", default=230)
    args = parser.parse_args()

    fsr = args.fsr

    if args.configFile:
	configFile = args.configFile

    cfg = scaleConfig.readConfig(configFile)

    if args.debug == None:
	DEBUG = cfg['raspberryPiConfig']['debug']
    else:
	DEBUG = args.debug

    alertState = shelve.open("scaleState.db", writeback=True)

    for alert in cfg['raspberryPiConfig']['alertChannels']:
        if alert not in alertState:
            alertState[alert] = 0
    alertState.sync()

    currentTime = str(datetime.datetime.now()).split('.')[0]

    processLowBeanAlerts (fsr, alertState, cfg, currentTime)
