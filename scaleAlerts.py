
def processAlerts (fsr, alertState, cfg, currentTime):

    # set the alertStates to 1 (alerted) and do the necessary
    # alerts if we seem to have too few beans
    if fsr < cfg['raspberryPiConfig']['getMoarBeansNow']:
        if DEBUG:
            print "uh oh, not enough beans"
        for alert in alertState:
            if alertState[alert] == 0:
                # this is where we would do the actual
                # alerts
                alertState[alert] = 1
                if DEBUG:
                    print "{0} Doing alert {1}".format(currentTime, alert)
                alertState.sync()

        # reset all of the alert channel states to 0 if we are 10%
        # above the bean limit and if we had previously set the alert
        # channel states
        if fsr > (cfg['raspberryPiConfig']['getMoarBeansNow'] * 1.1) and sum([alertState[m] for m in alertState]) > 0:
            for alert in alertState:
                alertState[alert] = 0
            alertState.sync()



if __name__ == "__main__":
    import yaml
    import shelve
    import scaleConfig
    import scaleTwitter
    import argparse
    import datetime

    configFile = './scaleConfig.yaml'

    parser = argparse.ArgumentParser()
    parser.add_argument ("-d", "--debug", type=int, choices=[0,1],
                         nargs='?', const=1,
                         help="turn debugging on (1) or off (0); this overrides"+
                         "the value in the configuration file ")
    parser.add_argument("-c","--config", action="store", dest="configFile",
                        help="specify a configuration file")
    args = parser.parse_args()

    if args.configFile:
	configFile = args.configFile

    cfg = scaleConfig.readConfig(configFile)

    if args.debug == None:
	DEBUG = cfg['raspberryPiConfig']['debug']
    else:
	DEBUG = args.debug

    alertState = shelve.open("scaleState", writeback=True)
    for alert in cfg['raspberryPiConfig']['alertChannels']:
        if alert not in alertState:
            alertState[alert] = 0
    alertState.sync()

    fsr = 230
    currentTime = str(datetime.datetime.now()).split('.')[0]


    processAlerts (fsr, alertState, cfg, currentTime)
