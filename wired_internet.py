#!/usr/bin/env python
import ipgetter
import re
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import sys,xmpp

from aux import *

# ahat: Important Note. xmpp package is broken. Must manullay edit file /usr/local/lib/python2.7/dist-packages/xmpp/transports.py
# and comment out lines 316 and 317
#        tcpsock._sslIssuer = tcpsock._sslObj.issuer()
#        tcpsock._sslServer = tcpsock._sslObj.server()


class WiredInternet( object ):
    """ This class handles emails and IM that must go out the wired internet route
    """
    COMMASPACE = ', '
    def __init__( self, mailParams, imParams ):
        self.mailParams = mailParams
        self.imParams = imParams

    def isAvailable( self ):
        """ Checks if wired internet is available by checking for a valid wan ip"""
        ip = ipgetter.myip()
        validIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        return re.match( validIpAddressRegex, ip ) is not None

    def email( self, mail ):
        msg = MIMEMultipart()
        msg['Subject'] = mail.subject
        msg['From'] = mail.From
        msg['To'] = WiredInternet.COMMASPACE.join( mail.To )
        msg.attach( MIMEText( mail.body, 'plain' ) )
        server = smtplib.SMTP( self.mailParams.server, self.mailParams.port )
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login( self.mailParams.username, self.mailParams.password )
        server.sendmail( mail.From, mail.To, msg.as_string() )
        server.quit()
        return True

    def im( self, iMessage ):
        jid = xmpp.protocol.JID( self.imParams.jid )
        cl = xmpp.Client( jid.getDomain(), debug=[] )
        con = cl.connect()
        if not con:
            print 'could not connect!'
            return False
        print 'connected with', con
        auth = cl.auth( jid.getNode(), self.imParams.password,resource = jid.getResource() )
        if not auth:
            print 'could not authenticate!'
            return False
        print 'authenticated using', auth

        #cl.SendInitPresence(requestRoster=0)   # you may need to uncomment this for old server
        for r in iMessage.recipients:
            id = cl.send(xmpp.protocol.Message( r, iMessage.message ) )
            print 'sent message with id', id

        time.sleep(1)   # some older servers will not send the message if you disconnect immediately after sending

        cl.disconnect()
        return True

    def execute( self, commands ):
        if( not self.isAvailable() ):
            return False
        for k, v in commands.iteritems():
            try:
                if( 'email' == k ):
                    self.email( v )
                elif( 'im' == k ):
                    if( not self.im( v ) ):
                        return False
            except:
                return False
        return True

if __name__ == "__main__":
    wi = WiredInternet( MailParams( 'ahatzikonstantinou@gmail.com', '645kk\\45', 'smtp.gmail.com', 587 ), InstantMessageParams( 'ahatziko.mainpc@gmail.com', '312ggp12' ) )
    print( wi.isAvailable() )
    # wi.email( EMail( "rpi-security", ["ahatzikonstantinou@gmail.com", "ahatzikonstantinou@silicontech.gr"], "mail test", "testing testing" ) )
    wi.im( InstantMessage( ['ahatzikonstantinou@gmail.com', 'ahatziko.master@gmail.com'], 'test3 im message' ) )