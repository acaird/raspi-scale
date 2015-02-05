import yaml
import sys, os

def readConfig (file):

    try:
        f = open(file)
    except:
        print "=========================== ERROR ==========================="
        print "I couldn't open the file '{0}'".format(file)
        print "to read the settings, so I'll have to think of"
        print "something else to do."
        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
        print "=========================== ERROR ==========================="
        exit (1)

    # this is list() to make the load_all generator generate
    # everything and put it into config before the file is close()'d
    configDocs = list(yaml.safe_load_all(f))
    f.close()

    # why safe_load_all makes an array is beyond me; I must be missing
    # something, because it makes the order of the YAML file matter,
    # and that's no good

    config = {}
    for doc in configDocs:
        config[doc['name']] = doc

    return(config)


if __name__ == "__main__":

    import pprint as pp

    configFile = './scaleConfig.yaml'

    cfg = readConfig(configFile)

    print "The debug setting is",cfg['raspberryPiConfig']['debug']

    print "And everything else is:"

    pp.pprint(cfg)
