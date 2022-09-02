__version__ = "2.0.4"

"""


EXAMPLES:

Normal login:
user = User('password', 'email')


Customized login:
user = User('password', 'email', smtp_server='smtp-mail.outlook.com', imap_server='imap-mail.outlook.com',
smtp_port=587, imap_port=993)

# Ports for SMTP and IMAP servers can be found at https://www.systoolsgroup.com/imap/.


Getting the latest mail:
user.mail_from_template(user.mail_from_id(user.mail_ids_as_str(1)[0]))

Sending an email:

user.sendmail('to_address', 'content', subject='subject', cc=[
              'cc_address1', 'cc_address2'], attachments=['file1.txt', 'file2.txt'])

Deleting 10 of the latest messages:
user.delete_mail(10)

Selecting a mailbox(mailboxes can be found from the User.list_mailboxes method):
user.select_mailbox('INBOX')

Saving all attachments from the latest message:
user.save_attachments(user.mail_from_id(user.mail_ids_as_str(1)[0]))

NOTE: to select mailboxes other than INBOX, you must select exactly how they are shown in the User.list_mailboxes method. Sent mailbox for example is shown as "[Gmail]/Sent Mail".
user.select_mailbox('"[Gmail]/Sent Mail"')
"""

# the rest of the methods are quite self-explanatory, if you need help DM me at HRLO77#3508 (discord) or HRLO77 (reddit)
# (Do the smart thing an open a discussion)

# Start the CLI by running - python -m CLImail -smtp_server [server] -imap_server [server] -smtp_port [smtp_port] -imap_port [imap_port]

# Or on unix- $python -m CLImail -smtp_server [server] -imap_server [server] -smtp_port [smtp_port] -imap_port [imap_port]
