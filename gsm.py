from aux import *

class SMS( object ):
    def __init__( self, phones, text ):
        self.text = text
        self.phones = phones

class GSM( object ):
    """ This class handles notifications that will be sent through the GSM interface
    """
    def __init__( self, mailParams, imParams ):
        self.mailParams = mailParams
        self.imParams = imParams
        
    def execute( self, commands ):
        """ Acceptable commands are email, im, sms, phonecall """
        pass #TODO