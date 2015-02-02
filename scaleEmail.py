import re
import sys, os
import yaml

def sendEmail (smtpServer, gmailCreds, fAddr, tAddr, subj, body):
    # https://docs.python.org/2/library/email-examples.html
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg['Subject'] = subj
    msg['From']    = fAddr
    msg['To']      = tAddr

    s = smtplib.SMTP(smtpServer)

    # We only need all this if we're authenticating to GMail, not if
    # we are using 'localhost' as the SMTP server.
    if re.search('gmail',smtpServer):
        '''
        the file 'gmailCreds.sec' is a text file that has two lines:
        <googleID>@gmail.com
        <gmail password or application specific password>
        with no indenting; only the first two lines are used, but all
        of the lines are read, so don't be too crazy with what's in
        there.
        '''
        creds=[]
        try:
            with open(gmailCreds) as f:
                creds = [x.strip('\n') for x in f.readlines()]
        except:
            print "=========================== ERROR ==========================="
            print "I couldn't open the file '{0}'".format(gmailCreds)
            print "to read your GMail login and password, so I can't send"
            print "email using the GMail SMTP server, and am giving up."
            print "(", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
            print "=========================== ERROR ==========================="
            exit (1)

        s.starttls()
        s.login(creds[0], creds[1])

    mailResults = {} # so we can comment out the next line and things still work
    mailResults = s.sendmail(fAddr, [tAddr], msg.as_string())
    s.quit()
    if (mailResults):
        return mailResults
    else:
        return 0

if __name__ == "__main__":

    emailConfigFile = './emailConfig.yaml'

    try:
        f = open(emailConfigFile)
    except:
        print "=========================== ERROR ==========================="
        print "I couldn't open the file '{0}'".format(emailConfigFile)
        print "to read the email settings, so I can't send email and"
        print "am giving up."
        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
        print "=========================== ERROR ==========================="
        exit (1)

    emailConfig = yaml.safe_load(f)
    f.close()

    subject  = "test email from Python"
    body     = '''
This is the test of my email message.  It is pretty boring, but
it is a few lines of text that will help me to see what different clients
do with this formatting.'''

    results = sendEmail (emailConfig['smtpServer'], emailConfig['gmailCreds'],
                         emailConfig['fromAddr'],   emailConfig['toAddr'],
                         subject, body)
    if (results):
        print "Delivery Failed, at least in part:",results
