import plotly.plotly as py
from plotly.graph_objs import *
import datetime
import sys,os

def updatePlot (timeAndDate,beanPercent,username,apiKey):
    py.sign_in(username,apiKey) # username, API key (not password)

    trace0 = Scatter (x=timeAndDate,
                      y=beanPercent)
    data = Data([trace0])

    title = "Coffee Bean Inventory<br>as of "+str(datetime.datetime.today()).split()[0]
    layout = Layout ( title=title,
                      xaxis=XAxis(title=''),
                      yaxis=YAxis(title='Bean Percentage',
                                  range=[0,100])
                  )

    fig = Figure(data=data, layout=layout)

    plot_url = py.plot(fig,
                       filename='CAENbeans',
                       fileopt='extend',
                       auto_open=False)

if __name__ == "__main__":

    import random
    import yaml

    plotlyConfigFile = './plotlyCreds.sec'

    try:
        f = open(plotlyConfigFile)
    except:
        print "=========================== ERROR ==========================="
        print "I couldn't open the file '{0}'".format(plotlyConfigFile)
        print "to read the plot.ly settings, so I can't make a plot and"
        print "am giving up."
        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
        print "=========================== ERROR ==========================="
        exit (1)

    plotlyConfig = yaml.safe_load(f)
    f.close()

    now = datetime.datetime.now()

    beans = random.random()*100

    updatePlot (now,beans,plotlyConfig['username'],plotlyConfig['apikey'])
