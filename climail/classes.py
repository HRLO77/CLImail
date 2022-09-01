import smtplib
import ssl
from collections import Counter
import imaplib
import email
import typing
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import base64
import inspect
import functools
import os
import colorama


# created a decorator that asserts whether or not the function arguments are of the corrent type, but it doesn't work with "typing" module typehints :(


def force(func):
    '''
    Forces annotation on arguments of functions.
    '''
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound_arguments = sig.bind(*args, **kwargs).arguments
        c = dict()
        for i, v in sig.parameters.items():
            if v.kind == v.POSITIONAL_OR_KEYWORD:
                if v.annotation != v.empty:
                    if not(isinstance(bound_arguments[v.name], v.annotation)):
                        c[v.name] = v.annotation(bound_arguments[v.name])
                    else:
                        c[v.name] = bound_arguments[v.name]
                else:
                    c[v.name] = bound_arguments[v.name]
            else:
                c[v.name] = bound_arguments[v.name]
        return func(**c)
    return wrapper


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

    def __init__(self, password: typing.AnyStr, user: typing.AnyStr, smtp_server: typing.AnyStr = "smtp.gmail.com", imap_server: typing.AnyStr = 'imap.gmail.com', smtp_port: typing.SupportsInt = 465, imap_port: typing.SupportsInt = 993):
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
        self.smtp_address = smtp_server
        self.imap_address = imap_server
        self.smtp_port = smtp_port
        self.imap_port = imap_port
        # print(user, password, server, imap_port, smtp_port, 'smtp.' + str(server))
        print('Starting SMTP server...')
        # spent two hours here only to find i made a typo :/
        self.smtp_server = smtplib.SMTP_SSL(
            str(smtp_server), int(smtp_port), context=context)
        print('Starting IMAP4 server...')
        self.imap_server = imaplib.IMAP4_SSL(
            str(imap_server), int(imap_port), ssl_context=context)
        print('Logging in and encrypting...')
        try:
            self.smtp_server.starttls(context=context)
            self.imap_server.starttls(ssl_context=context)
        except Exception:
            print('TLS encrytion failed.')
        self.smtp_server.ehlo_or_helo_if_needed(), self.imap_server.noop()  # can be omitted
        self.context = context
        self.imap_server.login(
            user, password), self.smtp_server.login(user, password)
        self.imap_server.noop()
        self.imap_server.select('INBOX', False)
        self.current_mailbox = 'INBOX'
        print('Done!')
        # requires error handling on login in case of invalid credentials or access by less secure apps is disabled.

    def sendmail(self, reciever: typing.AnyStr, content: typing.AnyStr = 'None', subject: typing.AnyStr = 'None', cc: typing.List[typing.AnyStr] = None, attachments: typing.List[typing.AnyStr] = None):
        '''
        Sends a basic email to a reciever and the cc.
        Currently doesn't support bcc's.
        '''
        # TODO: add support for bcc's
        msg = MIMEMultipart()
        r = [reciever, *cc] if not cc is None else reciever
        msg['To'] = reciever
        msg['Date'] = formatdate(localtime=True)
        msg['Cc'] = COMMASPACE.join(cc) if not cc is None else 'None'
        msg['From'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))
        if not attachments is None:
            print('loading attachments')
            attachments = [open(i, 'rb') for i in attachments]
            for attachment in attachments:  # add the attachments
                part = MIMEApplication(
                    attachment.read(),
                    Name=os.path.basename(attachment.name))
                part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(
                    attachment.name)
                msg.attach(part)
        text = msg.as_string()
        self.smtp_server.sendmail(self.email, r, text)
        return True  # Message has been sent succesfully!

    def rename_mailbox(self, old: typing.AnyStr, new: typing.AnyStr):
        '''
        Renames a mailbox.
        '''
        self.imap_server.rename(old, new)
        return True  # Mailbox has been renamed succesfully!

    def search(self, string: typing.AnyStr = None, requirements: typing.AnyStr = '(UNSEEN)', size: typing.SupportsInt = 10):
        '''
        Looks for mail with the string provided and requirements as a tuple of bytes.
        '''
        return tuple(self.imap_server.search(string, requirements)[1][0].split()[-1:0-(size+1):-1])

    def subscribe(self,
                  mailbox: typing.AnyStr):  # and don't forget to hit that like button and click the notificaion bell for more!
        '''
        Subscribes to a mail box.
        '''
        self.imap_server.subscribe(mailbox)
        return True  # successfully subscribed

    def unsubscribe(self, mailbox: typing.AnyStr):
        '''
        Unsubscribes to a mail box.
        '''
        self.imap_server.unsubscribe(mailbox)
        return True  # successfully unsubscribed

    def create_mailbox(self, mailbox: typing.AnyStr):
        '''
        Creates a mailbox.
        '''
        self.imap_server.create(mailbox)
        return True  # Created a mailbox!

    def delete_mailbox(self, mailbox: typing.AnyStr):
        '''
        Deletes a mailbox.
        '''
        self.imap_server.delete(mailbox)
        return True  # deleted a mailbox

    def mail_ids_as_str(self, size: typing.SupportsInt = -1):
        '''
        Returns the ID's of the mails specified as a tuple of strings.
        '''
        r, mails = self.imap_server.search(None, 'ALL')
        return tuple(mails[0].decode().split()[-1:0-(size+1):-1])

    def mail_ids_as_bytes(self, size: typing.SupportsInt = -1):
        '''
        Returns the ID's of the mails specified as a tuple of bytes.
        '''
        r, mails = self.imap_server.search(None, 'ALL')
        return tuple((mails[0].split()[-1:0-(size+1):-1]))

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

    def mail_from_id(self, id: typing.Union[typing.ByteString, typing.AnyStr]) -> email.message.Message:
        '''
        Returns the mail from specified ID, ID can be found with User.mail_ids_as_str method.
        Use User.mail_from_template method to convert the mail to a string template.
        '''
        m=email.message_from_bytes(
            self.imap_server.fetch(str(id), '(RFC822)')[1][0][1])
        setattr(m, 'id', id)
        return m  # I hate working with bytes

    def mail_from_ids(self, ids: typing.Iterable[typing.Union[typing.ByteString, typing.AnyStr]]) -> typing.Generator:
        '''
        Takes an iterable of string or bytes ID's and returns a generator of email.message.Message objects.
        '''
        for i in ids:
            m=email.message_from_bytes(
            self.imap_server.fetch(str(i), '(RFC822)')[1][0][1])
            setattr(m, 'id', i)
            yield m

    @force
    def mail_from_template(self, message: email.message.Message):
        '''
        Takes a email.message.Message object (object can be found from User.mail_from_id method) and creates a message out of a template for it. (Not sure if template is the right word.)
        You can change this method to create a template that looks better, your choice.
        '''
        string = '================== Start of Mail ====================\n'
        if 'message-id' in message:
            string += f'ID:        {message["message-id"]}\n'
        string += f'Server-ID: {message.id}\n'
        string += f'From:      {message["From"]}\n'
        string += f'To:        {message["To"]}\n'
        string += f'Cc:        {message["Cc"]}\n'
        string += f'Bcc:       {message["Bcc"]}\n'
        string += f'Date:      {message["Date"]}\n'
        string += f'Subject:   {message["subject"]}\n'
        for i in message.walk():
            if isinstance(i, str):
                s = i
                l = list()
                for b in s.split(' '):
                    try:
                        l.append(base64.b64decode(b.removeprefix('base64').replace(
                            '\n', '')).decode('utf-8'))
                    except Exception:
                        l.append(b)
                string += f'\nBody:\n\n{" ".join(l)}\n'
                break
            if i.get_content_type() == "text/plain":
                s = i.as_string()
                l = list()
                for b in s.split(' '):
                    try:
                        l.append(base64.b64decode(b.removeprefix('base64').replace(
                            '\n', '')).decode('utf-8'))
                    except Exception:
                        l.append(b)
                string += f'\nBody:\n\n{" ".join(l)}\n'
        string += '\n\nAttachments:\n'
        for n in message.get_payload():
            if isinstance(n, str):
                continue
            if n.get_content_type().startswith('application') or n.get_content_type().startswith('image'):
                string += f'{n.get_filename()}\n'
        string += '\n================== End of Mail ======================\n'
        return string

    def save_attachments(self, message: email.message.Message, path: typing.AnyStr = r'\tmp') -> typing.Generator:
        '''
        Saves all attachments of an email to the directory specified, returns a generator of paths.
        '''
        colorama.init(True)
        for n in message.get_payload():
            if isinstance(n, str):
                continue
            if n.get_content_type().startswith('application') or n.get_content_type().startswith('image'):
                name = n.get_filename().replace(' ', '_')
                p = os.path.join(path, name)
                p.replace('/', '\\')
                if not os.path.isdir(path):
                    os.mkdir(path)
                if not os.path.isfile(p):
                    with open(p, 'wb') as fp:
                        fp.write(n.get_payload(decode=True))
                yield p

    def select_mailbox(self, mailbox: typing.AnyStr, readonly: bool = False):
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
        del self.smtp_server
        del self.imap_server
        print('Successfully logged out.')

    def list_mailboxes(self):
        '''
        Lists all mailboxes for the current user.
        '''
        return self.imap_server.list()[1]

    def delete_mail_ids(self, ids: typing.List[typing.AnyStr or typing.ByteString]):
        '''
        Moves specified mail ID's to the trash.
        Ids: An iterable of strings or bytestrings to move to trash.
        '''
        for v in self.mail_from_ids(ids):
            self.imap_server.store(v, '+FLAGS', '\\Deleted')
        print(f'Deleted {len(ids)} messages.')

    def delete_mail(self, size: typing.SupportsInt = 10):
        '''
        Moves amount of mail specified to the trash.
        Size: The amount of last emails in the current mailbox to move to trash
        '''
        for i in self.mail_from_ids(self.mail_ids_as_str()[-1:0-(size+1):-1]):
            self.imap_server.store(i, '+FLAGS', '\\Deleted')
        print(f'Deleted {size} messages.')

    def clear(self):
        '''
        Expunges all deleted mail in the current mailbox.
        '''
        self.imap_server.expunge()
        print('Cleared all trash.')

    def contacts(self, size: typing.SupportsInt = 10):
        '''
        Returns a tuple of recent contacts in the current mailbox.
        Size: The amount of last emails to check for contacts in the current mailbox.
        '''
        mails = tuple(self.mail_from_id(i) for i in self.mail_ids_as_str(size))
        contacts = list()
        for i in mails:
            if 'To' in i:
                for b in i['To'].split(','):
                    t = b.removesuffix(
                        '>').removeprefix('<') if not ' ' in b else b.rsplit(' ')[-1].removesuffix(
                        '>').removeprefix('<')
                    if not(self.email == t):
                        contacts.append(t)
            if 'From' in i:
                for b in i['From'].split(','):
                    t = b.removesuffix(
                        '>').removeprefix('<') if not ' ' in b else b.rsplit(' ')[-1].removesuffix(
                        '>').removeprefix('<')
                    if not(self.email == t):
                        contacts.append(t)
        c = Counter(contacts)

        return tuple(i[0] for i in c.most_common())

    def reconnect(self):
        '''
        Attempts to close, and reconnect to the IMAP and SMTP servers with details provided at instantiation.
        '''
        # print(user, password, server, imap_port, smtp_port, 'smtp.' + str(server))
        try:
            self.smtp_server.quit()
            self.smtp_server.close()
            self.imap_server.close()
            self.imap_server.logout()
            del self.smtp_server
            del self.imap_server
        except Exception:
            print('Could not properly close servers.')
        else:
            print('Closed servers.')
        print('Restarting SMTP server...')
        self.smtp_server = smtplib.SMTP_SSL(
            'smtp.' + str(self.smtp_address), int(self.smtp_port), context=self.context)
        print('Restarting IMAP4 server...')
        self.imap_server = imaplib.IMAP4_SSL(
            'imap.' + str(self.imap_address), int(self.imap_port), ssl_context=self.context)
        print('Logging in and encrypting...')
        try:
            self.smtp_server.starttls(context=self.context)
            self.imap_server.starttls(ssl_context=self.context)
        except Exception:
            print('TLS encrytion failed.')
        self.smtp_server.helo(), self.smtp_server.ehlo()  # can be omitted
        self.context = self.context
        self.imap_server.login(
            self.email, self.password), self.smtp_server.login(self.email, self.password)
        self.imap_server.noop()
        self.imap_server.select('INBOX', False)
        self.current_mailbox = 'INBOX'
        print('Done!')

    def copy_mails(self, ids: typing.Iterable[typing.AnyStr or typing.ByteString], folder: typing.AnyStr):
        '''
        Copies mail ids to new folder
        Ids: An iterable of strings or bytestrings of mail ids.
        Folder: A string for the name of the folder to copy mail ids to.
        '''
        self.imap_server.copy(':'.join(ids), folder)
        
    def restore_id(self, id: typing.AnyStr or typing.ByteString):
        '''Restores an email by ID from trash.'''
        self.imap_server.store(self.mail_from_id(id), '-FLAGS', '\\Deleted')
        print(f'Restored mail ID {id}.')
        
    def restore_ids(self, ids: typing.Iterable[typing.AnyStr or typing.ByteString]):
        '''Restores an email by ID from trash.'''
        for i in ids:
            self.imap_server.store(self.mail_from_id(i), '-FLAGS', '\\Deleted')
        print(f'Restored {len(ids)} emails.')


