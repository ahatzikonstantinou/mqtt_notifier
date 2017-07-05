from aux import *

class GSM( object ):
    """ This class handles notifications that will be sent through the GSM interface
    """
    def __init__( self, mailParams, imParams ):
        self.mailParams = mailParams
        self.imParams = imParams
        
    def execute( self, comands ):
        """ Acceptable commands are email, im, sms, phonecall """
        pass #TODO