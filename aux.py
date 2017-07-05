class InstantMessage( object ):
    def __init__( self, recipients, message ):
        self.recipients = recipients
        self.message = message

class InstantMessageParams( object ):
    def __init__( self, jid, password ):
        self.jid = jid
        self.password = password

class EMail( object ):
    def __init__( self, From, To, subject, body ):
        self.From = From
        self.To = To
        self.subject = subject
        self.body = body

class MailParams( object ):
    def __init__( self, username, password, server, port ):
        self.username = username
        self.password = password
        self.server = server
        self.port = port