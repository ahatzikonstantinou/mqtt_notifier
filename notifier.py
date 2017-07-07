#!/usr/bin/env python
import paho.mqtt.client as mqtt  #import the client1
import signal   #to detect CTRL C
import sys

import json #to generate payloads for mqtt publishing
import jsonpickle #json.dumps crashes for InstantMessage. jsonpickle works fine
import os.path # to check if configuration file exists

from gsm import *
from wired_internet import *

class MqttParams( object ):
    """ Holds the mqtt connection params
    """
    def __init__( self, address, port, subscribeTopic, publishTopic ):
        self.address = address
        self.port = port
        self.subscribeTopic = subscribeTopic
        self.publishTopic = publishTopic

class Notifier( object ):
    """ This class handles notifications such as phonecalls, sms, email and IM
    """
    def __init__( self, mqttId, mqttParams, mailParams, imParams ):        
        self.mqttParams = mqttParams
        self.mqttId = mqttId
        self.gsm = GSM( mailParams, imParams )
        self.wi = WiredInternet( mailParams, imParams )

        signal.signal( signal.SIGINT, self.__signalHandler )

    def run( self ):
        #create a mqtt client
        self.client = mqtt.Client( self.mqttId )
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        #set last will and testament before connecting
        self.client.will_set( self.mqttParams.publishTopic, json.dumps({ 'main': 'UNAVAILABLE' }), qos = 1, retain = True )
        self.client.connect( self.mqttParams.address, self.mqttParams.port )
        self.client.loop_start()
        #go in infinite loop
        while( True ):
            pass

    def __signalHandler( self, signal, frame ):
        print('Ctrl+C pressed!')
        self.client.disconnect()
        self.client.loop_stop()
        sys.exit(0)        

    def __on_connect( self, client, userdata, flags_dict, result ):
        """Executed when a connection with the mqtt broker has been established
        """
        #debug:
        m = "Connected flags"+str(flags_dict)+"result code " + str(result)+"client1_id  "+str(client)
        print( m )

        # tell other devices that the notifier is available
        self.client.will_set( self.mqttParams.publishTopic, json.dumps({ 'main': 'AVAILABLE' }), qos = 1, retain = True )
        
        #subscribe to start listening for incomming commands
        self.client.subscribe( self.mqttParams.subscribeTopic )

    def __on_message( self, client, userdata, message ):
        """Executed when an mqtt arrives

        cmd format: 
            "email": { "from": "sender", "to": "recipient", "subject": "the subject", "body": "the body" }
            "im": { "recipients": [ "jabber id of each recipient e.g. user@gmail.com" ], "message": "the message" }
            "phonecall": [ phonenumber1, phonenumber2, ..., phonenumberN  ]
            "sms": { "text": "the message", "phones": [ phonenumber1, phonenumber2, ..., phonenumberN  ] }
        """
        text = message.payload.decode( "utf-8" )
        print( 'Received message "{}"'.format( text ).encode( 'utf-8' ) )
        if( mqtt.topic_matches_sub( self.mqttParams.subscribeTopic, message.topic ) ):            
            try:
                cmds = json.loads( text )
            except ValueError, e:
                print( '"{}" is not a valid json text, exiting.'.format( text ) )
                return
            gsmCmds = []
            wiCmds = []
            if( 'email' in cmds and cmds[ 'email' ] is not None ):
                #note: Email.To param must be a list of recipients (even if it contains only one element )
                wiCmds[ 'email' ] = EMail( cmds[ 'email' ][ 'From' ], cmds[ 'email' ][ 'To' ], cmds[ 'email' ][ 'subject' ], cmds[ 'email' ][ 'body' ] )
            if( 'im' in cmds and cmds[ 'im' ] is not None ):
                # wiCmds[ 'im' ] = InstantMessage( cmds[ 'im' ][ 'recipients' ], cmds[ 'im' ][ 'message' ] )
                wiCmds[ 'im ' ] = jsonpickle.decode( json.dumps( cmds[ 'im' ] ) )
                TODO

            #if wi is not available and cannot execute the commands, have gsm execute them
            if( not self.wi.execute( wiCmds ) ):
                gsmCmds.update( wiCmds );

            if( 'phonecall' in cmds  and cmds[ 'phonecall' ] is not None ):
                gsmCmds[ 'phonecall' ] = cmds[ 'phonecall' ]

            if( 'sms' in cmds and cmds[ 'sms' ] is not None ):
                gsmCmds[ 'sms' ] = SMS( cmds[ 'sms' ][ 'text' ], cmds[ 'sms' ][ 'phones' ] )

            self.gsm.execute( cmds )

if( __name__ == '__main__' ):
    configurationFile = 'notifier.conf'
    if( not os.path.isfile( configurationFile ) ):
        print( 'Configuration file "{}" not found, exiting.'.format( configurationFile ) )
        sys.exit()

    with open( configurationFile ) as json_file:
        configuration = json.load( json_file )
        print( 'Configuration: \n{}'.format( json.dumps( configuration, indent = 2  ) ) )
        

        notifier = Notifier( 
            configuration['mqttId'],
            MqttParams( configuration['mqttParams']['address'], int( configuration['mqttParams']['port'] ), configuration['mqttParams']['subscribeTopic'], configuration['mqttParams']['publishTopic'] ),
            MailParams( configuration['mailParams']['user'], configuration['mailParams']['password'], configuration['mailParams']['server']['url'], configuration['mailParams']['server']['port'] ), 
            InstantMessageParams( configuration['instantMessageParams']['user'], configuration['instantMessageParams']['password'] )
        )

        notifier.run()