import smtplib
import ssl
from os.path import basename
import imaplib
import email
import typing
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
import base64


class User:
    '''
    Represents an email account.
    Requires a password and user email for instantiation.
    Account must have "less secure apps allowed" enabled in account settings.
    NOTE: ADD MORE ERROR HANDLING!!!
    '''

    # TODO: Implement more features from smtplib and imaplib, maybe consider using poplib.

    def __eq__(self, other):
        return self.email == other.email and self.password == other.password and self.port == other.port and isinstance(
            other, self.__class__)  # dunno why I added this function

    def __init__(self, password: str, user: str, server: str = "gmail.com", smtp_port: int = 465, imap_port: int = 993):
        '''
        All ports and server options available at https://www.systoolsgroup.com/imap/.
        Check it out yourself.
        '''
        '''
        IMAP: imap.gmail.com - 993
        SMTP: smtp.gmail.com - 465
        '''
        context = ssl.create_default_context()
        self.email = user
        self.password = password
        # print(user, password, server, imap_port, smtp_port, 'smtp.' + str(server))
        print('Starting SMTP server...')
        # spent two hours here only to find i made a typo :/
        self.smtp_server = smtplib.SMTP_SSL(
            'smtp.' + str(server), int(smtp_port), context=context)
        print('Starting IMAP server...')
        self.imap_server = imaplib.IMAP4_SSL(
            'imap.' + str(server), int(imap_port), ssl_context=context)
        print('Logging in and encrypting...')
        try:
            self.smtp_server.starttls(context=context)
            self.imaplib_server.starttls(ssl_context=context)
        except Exception:
            print('TLS encrytion failed.')
        self.smtp_server.ehlo()  # can be omitted
        self.context = context
        self.imap_server.login(
            user, password), self.smtp_server.login(user, password)
        self.imap_server.select('INBOX', False)
        self.current_mailbox = 'INBOX'
        print('Done!')
        # requires error handling on login in case of invalid credentials or access by less secure apps is disabled.

    def sendmail(self, reciever: str, content: str = 'None', subject: str = 'None', cc: typing.List[typing.AnyStr] = None, attachments: typing.List[typing.AnyStr] = None):
        '''
        Sends a basic email to a reciever and the cc.
        Currently doesn't support bcc's.
        '''
        # TODO: add support for bcc's
        self.smtp_server.set_debuglevel(1)
        msg = MIMEMultipart()
        r = [reciever, *cc] if not cc is None else reciever
        msg['To'] = reciever
        msg['Date'] = formatdate(localtime=True)
        msg['Cc'] = COMMASPACE.join(cc)
        msg['From'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))
        if not attachments is None:
            print('loading attachments')
            attachments = [open(i, 'rb') for i in attachments]
            for attachment in attachments:  # add the attachments
                part = MIMEApplication(
                    attachment.read(),
                    Name=attachment.name)
                part['Content-Disposition'] = 'attachment; filename="%s"' % attachment.name
                msg.attach(part)
        text = msg.as_string()
        self.smtp_server.sendmail(self.email, r, text)
        return True  # Message has been sent succesfully!

    def rename_mailbox(self, old: str, new: str):
        '''
        Renames a mailbox.
        '''
        self.imap_server.rename(old, new)
        return True  # Mailbox has been renamed succesfully!

    def search(self, string: str = None, requirements: str = '(UNSEEN)', size: int = 10):
        '''
        Looks for mail with the string provided and requirements.
        '''
        print(string, requirements)
        return self.imap_server.search(string, requirements)[1][0].decode().split()[:size]

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

    def mail_ids_as_str(self, size: int = -1):
        '''
        Returns the ID's of the mails specified as a tuple of strings.
        '''
        r, mails = self.imap_server.search(None, 'ALL')
        return tuple(mails[0].decode().split()[:0-(size+1):-1].__reversed__())

    def mail_ids_as_bytes(self, size: int = -1):
        '''
        Returns the ID's of the mails specified as a tuple of bytes.
        '''
        r, mails = self.imap_server.search(None, 'ALL')
        return tuple((mails[0].split()[:0-(size+1):-1].__reversed__()))

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
        Returns the mail from specified ID, ID can be found with User.mail_ids_as_str method.
        Use User.mail_from_template method to convert the mail to a string template.
        '''

        return email.message_from_bytes(
            self.imap_server.fetch(str(id), '(RFC822)')[1][0][1])  # I hate working with bytes

    def mail_from_template(self, message: email.message.Message):
        '''
        Takes a email.message.Message object (object can be found from User.mail_from_id method) and creates a message out of a template for it. (Not sure if template is the right word.)
        You can change this method to create a template that looks better, your choice.
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
                s = i.as_string()
                l = list()
                for i in s.split(' '):
                    try:
                        l.append(base64.b64decode(i.removeprefix('base64').replace(
                            '\n', '')).decode('utf-8'))
                    except BaseException:
                        l.append(i)
                string += f'\nBody:\n\m{" ".join(l)}\n'
                break
        string += '\n\nAttachments:\n'
        for i in message.get_payload():
            if i.get_content_type() == 'text/plain':
                continue
            string += f'{i.get_filename()}\n'
        string += '\n================== End of Mail ======================\n'
        return string

    def select_mailbox(self, mailbox: str, readonly: bool = False):
        '''
        Selects a mailbox. (All actions pertaining to a mailbox in User.imap_server are affecting the selected mailbox, INBOX, is the default)
        '''
        if mailbox in str(self.imap_server.list()[1]):
            self.imap_server.select(mailbox, readonly)
            self.current_mailbox = mailbox
            return True  # Sucessfully selected a mailbox!
        return False

    def unselect_mailbox(self):
        '''
        Unselects a mailbox, explaination is given in the User.select_mailbox method. The current mailbox will be unselected, not reset to INBOX, but unselected until User.select_mailbox method is used.
        '''
        self.imap_server.unselect()
        self.current_mailbox = 'None'
        return True  # succesfully unselected the current mailbox.

    def refresh(self):
        '''
        Refreshes the current mailbox and fetches new mails.
        '''
        self.imap_server.unselect()
        return self.select_mailbox(self.current_mailbox)

    def close(self):
        '''
        Closes SMTP and IMAP servers, logs out and deletes user data.
        It is recommended to run this method before exiting the program.
        '''
        self.smtp_server.quit()
        self.imap_server.close()
        self.imap_server.logout()
        del self.password
        del self.email
        print('Successfully logged out.')

    def list_mailboxes(self):
        '''
        Lists all mailboxes for the current user.
        '''
        return self.imap_server.list()[1]

    def delete_mail_ids(self, ids: typing.List[int]):
        '''
        Moves specified mail ID's to the trash.
        '''
        for i in ids:
            self.imap_server.store(i, '+FLAGS', '\\Deleted')
        print(f'Deleted {len(ids)} messages.')

    def delete_mail(self, size: int = 10):
        '''
        Moves amount of mail specified to the trash.
        '''
        for i in self.mail_ids_as_str()[:0-(size+1):-1].__reversed__():
            self.imap_server.store(i, '+FLAGS', '\\Deleted')
        print(f'Deleted {size} messages.')

    def clear(self):
        '''
        Expunges all deleted mail in the current mailbox.
        '''
        self.imap_server.expunge()
        print('Cleared all trash.')


'''


EXAMPLES:

Normal login:
user = User('password', 'email')


Customized login:
user = User('password', 'email', server='smtp.outlook.com',
            smtp_port=587, imap_port=993)

# Ports for SMTP and IMAP servers can be found at https://www.systoolsgroup.com/imap/.


Getting the latest mail:
user.mail_from_template(user.mail_from_id(user.mail_ids_as_str(-1)[-1]))

Sending an email:

user.sendmail('to_address', 'content', subject='subject', cc=[
              'cc_address1', 'cc_address2'], attachments=['file1.txt', 'file2.txt'])

Deleting 10 of the latest messages:
user.delete_mail(10)

Selecting a mailbox(mailboxes can be found from the User.list_mailboxes method):
user.select_mailbox('INBOX')

NOTE: to select mailboxes other than INBOX, you must select exactly how they are shown in the User.list_mailboxes method. Sent mailbox for example is shown as "[Gmail]/Sent Mail".
user.select_mailbox('"[Gmail]/Sent Mail"')
'''

# the rest of the methods are quite self-explanatory, if you need help DM me at HRLO77#3508 (discord) or HRLO77 (reddit)
# (Do the smart thing an open a discussion)

# start the CLI by running - python CLImail -server [server] -smtp_port [smtp_port] -imap_port [imap_port]
# or on unix- $python CLImail -server [server] -smtp_port [smtp_port] -imap_port [imap_port]
