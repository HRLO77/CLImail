import smtplib, ssl, imaplib, email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import typing


class User:
    '''
    Represents a useer.
    Requires a password and user email for instantiation.
    Account must have "less secure apps allowed" enabled in account settings.
    NOTE: ADD MORE ERROR HANDLING!!!
    '''

    # TODO: Implement more features from smtplib and imaplib, maybe consider using poplib.

    def __eq__(self, other):
        return self.email == other.email and self.password == other.password and self.port == other.port and isinstance(
            other, self.__class__)  # dunno why I added this function

    def __init__(self, password: str, user: str, server: str = 'gmail.com', smtp_port: int = 465, imap_port: int = 993):
        '''
        Too lazy to add support for other email providers.
        All ports and server options available at https://www.systoolsgroup.com/imap/.
        Check it out youself.
        '''
        # TODO: add support for different emails such at outlook, hotmail, and maybe organization emails
        '''
        IMAP: imap.gmail.com - 993
        SMTP: smtp.gmail.com - 465
        '''
        context = ssl.create_default_context()
        self.email = user
        self.password = password
        self.smtp_server = smtplib.SMTP_SSL('smtp.' + str(server), int(smtp_port),
                                            context=context)  # spent two hours here only to find i made a typo :/
        self.imap_server = imaplib.IMAP4_SSL('imap.' + str(server), int(imap_port), ssl_context=context)
        self.smtp_server.ehlo()  # can be omitted
        self.context = context
        self.imap_server.login(user, password), self.smtp_server.login(user, password)
        self.imap_server.select('INBOX', False)
        # requires error handling on login in case of invalid credentials or access by less secure apps is disabled.

    def sendmail(self, reciever: str, content: str = 'None', subject: str = 'None', cc: typing.List = None):
        '''
        Sends a basic email to a reciever and the cc.
        Currently doesn't support bcc's and attachments.
        '''
        # TODO: add support for bcc's and attachment of files
        msg = MIMEMultipart()
        if not cc is None:
            r = [reciever, *cc]
            msg['To'] = ", ".join(r)
        else:
            r = reciever
            msg['To'] = r
        msg['From'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))
        # attachments = [open(i, 'r') for i in attachments]
        # for attachment in attachments: # add the attachments
        #     payload = MIMEBase('application', 'octate-stream')
        #     payload.set_payload((attachment).read())
        #     email.encoders.encode_base64(payload)
        #     payload.add_header('Content-Decomposition', 'attachment', filename=attachment.name)
        #     msg.attach(payload)
        '''
        Code above is commented out because of errors I am yet to understand.
        '''
        text = msg.as_string()
        print(text)
        self.smtp_server.sendmail(self.email, r, text)
        return True  # Message has been sent succesfully!

    def rename_mailbox(self, old: str, new: str):
        '''
        Renames a mailbox.
        '''
        self.imap_server.rename(old, new)
        return True  # Mailbox has been renamed succesfully!

    def search(self, string: str, requirements: str):
        '''
        Looks for mail with the string provided and requirements.
        '''
        try:
            return self.imap_server.search(string, requirements)[1][0].decode().split()
        except BaseException as e:  # too lazy to list actual exception
            return f'An error occurred: \n {e}\n'

    def subscribe(self,
                  mailbox: str):  # and don't forget to hit that like button and click the notificaion bell for more!
        '''
        Subscribes to a mail box.
        '''
        self.imap_server.subscribe(mailbox)
        return True  # successfully subscribed

    def unsubscribe(self, mailbox: str):
        '''
        Unsubscribes to a mail box.
        '''
        self.imap_server.unsubscribe(mailbox)
        return True  # successfully unsubscribed

    def create_mailbox(self, mailbox: str):
        '''
        Creates a mailbox.
        '''
        self.imap_server.create(mailbox)
        return True  # Created a mailbox!

    def delete_mailbox(self, mailbox: str):
        '''
        Deletes a mailbox.
        '''
        self.imap_server.delete(mailbox)
        return True  # deleted a mailbox

    def check_mail(self, size: int=-1):
        '''
        Returns the ID's of the mails specified.
        '''
        r, mails = self.imap_server.search(None, 'ALL')
        return mails[0].decode().split()[:int(size)]

    def is_unread(self):
        '''
        Returns True if current user has unread messages, otherwise False.
        '''
        (retcode, messages) = self.imap_server.search(None, '(UNSEEN)')
        if retcode == 'OK':
            if len(messages[0].split()) > 0:
                return True
            else:
                return False

    def mail_from_id(self, id: str):
        '''
        Returns the mail in BYTES from specified ID, ID can be taken with User.check_mail method.
        Use email.message_from_bytes method to convert the mail to email.message.Message.
        Retrieve data using message.get("From"), message.get("Date") for instance._
        '''
        return email.message_from_bytes(
            self.imap_server.fetch(str(id), '(RFC822)')[1][0][1])  # I hate working with bytes

    def mail_from_template(self, message: email.message.Message):
        '''
        Takes a email.message.Message object and creates a message out of a template for it. (Not sure if template is the right word.)
        '''
        string = '================== Start of Mail ====================\n'
        string += f'From:    {message.get("From")}\n'
        string += f'To:      {message.get("To")}\n'
        string += f'Cc:      {message.get("Cc")}\n'
        string += f'Bcc:     {message.get("Bcc")}\n'
        string += f'Date:    {message.get("Date")}\n'
        string += f'Subject: {message.get("Subject")}\n'
        for i in message.walk():
            if i.get_content_type() == "text/plain":
                string += i.as_string()
        string += '\n================== End of Mail ======================\n'
        return string

    def select_mailbox(self, mailbox: str, readonly: bool = True):
        '''
        Selects a mailbox. (All actions pertaining to a mailbox in User.imap_server are affecting the selected mailbox, INBOX, is the default)
        '''
        self.imap_server.select(mailbox, readonly)
        return True  # Sucessfully selected a mailbox!

    def unselect_mailbox(self):
        '''
        Unselects a mailbox, explaination is given in the User.select_mailbox method. The current mailbox will be unselected, not reset to INBOX, but unselected until User.select_mailbox method is used.
        '''
        self.imap_server.unselect()
        return True  # succesfully unselected the current mailbox.

    def close(self):
        '''
        Closes SMTP and IMAP3 servers, logs out and deletes user data.
        '''
        self.smtp_server.quit()
        self.imap_server.close()
        self.imap_server.logout()
        del self.password
        del self.email

    def list_mailboxes(self):
        '''
        Lists all mailboxes for the current user.
        '''
        return self.imap_server.list()[1]


'''
EXAMPLES:

Normal login:
user = User('password', 'email')


Customized login:
user = User('password', 'email', server='outlook.com', smtp_port=587, imap_port=993) # ports for smtp and imap servers can be found at https://www.systoolsgroup.com/imap/.


Getting the latest mail:
user.mail_from_template(user.mail_from_id(user.check_mail(None)[-1]))

Sending an email:

user.sendmail('to_address', 'content', subject='subject', cc=['cc_address1', 'cc_address2'])
'''

# the rest of the methods are quite self-explanatory, if you need help DM me at HRLO77#3508 (discord) or HRLO77 (reddit)
# (Do the smart thing an open a discussion)

# start the CLI by running - python CLImail <email_address> <password> -server [server] -smtp_port [smtp_port] -imap_port [imap_port]
# or on unix- $python CLImail <email_address> <password> -server [server] -smtp_port [smtp_port] -imap_port [imap_port]
