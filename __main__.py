import argparse
import sys
import climail
import argparse

my_parser = argparse.ArgumentParser(description='A CLI email client.', prog='CLImail')
# Add the arguments
my_parser.add_argument('Email',
                       metavar='user',
                       type=str,
                       help='The email to sign in as.')
my_parser.add_argument('Password',
                       metavar='password',
                       type=str,
                       help='The password to sign in to the email with.')
my_parser.add_argument('-server',
                       metavar='server',
                       type=str,
                       help='The server to sign in with, i.e gmail.com or outlook.com',
                       default='gmail.com',
                       required=False)
my_parser.add_argument('-smtp_port',
                       metavar='smtp_port',
                       type=str,
                       help='The port to sign into the SMTP server with, is defaulted to 465',
                       default=465,
                       required=False)
my_parser.add_argument('-imap_port',
                       metavar='imap_port',
                       type=str,
                       help='The port to sign into the IMAP3 server with, is defaulted to 993',
                       default=993,
                       required=False)

# Execute the parse_args() method
args = my_parser.parse_args()

password = args.Password
user = args.Email
try:
    U = climail.User(password, user, server=args.server, imap_port=args.imap_port, smtp_port=args.smtp_port) # login
except BaseException as e:
    print(e)
    my_parser.exit()
else:
    print('Logged in as', user)
while True:
    try:
        '''
        BE WARNED: this is very ugly - I probably wrote this code while drunk because I have no clue how I did it.
        (I know i can use click but i don't wanna)
        '''
        parser = argparse.ArgumentParser(description='A CLI email client.', prog='CLImail')
        cmd = input('>>>')
        subparsers = parser.add_subparsers()
        help = subparsers.add_parser('help',
                                               help='Shows this message.')
        help.set_defaults(func=lambda: parser.print_help())
        selectmail = subparsers.add_parser('selectmailbox', aliases=['select_mailbox', 'select'],
                                               help='Selects a mailbox.')
        selectmail.add_argument('-mailbox', required=True, help='The mailbox to select.', type=str)
        selectmail.add_argument('-readonly', required=False, help='Readonly mode or not.', type=bool, default=True)
        selectmail.set_defaults(func=lambda: U.select_mailbox(args.mailbox, args.readonly))
        cancelmailbox = subparsers.add_parser('unselect', aliases=['unselect_mailbox', 'cancel_mailbox'],
                                               help='Unselects the current mailbox.')
        cancelmailbox.set_defaults(func=lambda: U.unselect_mailbox())
        list_mailboxes = subparsers.add_parser('listmailboxes', aliases=['lmb', 'mailboxes'],
                                               help='Lists all of the mail boxes the current user has.')
        list_mailboxes.set_defaults(func=lambda: print(U.list_mailboxes()))
        sendmail = subparsers.add_parser('sendmail', aliases=['send', 'sendmessage'],
                                               help='Sends a message.')
        sendmail.add_argument('-reciever', help='The address to mail.', required=True)
        sendmail.add_argument('-content', help='Body of the message.', required=True)
        sendmail.add_argument('-subject', help='The subject', required=False)
        sendmail.add_argument('-cc', help='Carbon copy - addresses to send the mail to as well.', required=False, type=list)
        sendmail.set_defaults(func=lambda: (U.sendmail(args.reciever, args.content, args.subject, args.cc), print(f'Email sent to {args.reciever} successfully!')))
        unread = subparsers.add_parser('unread', aliases=['unreads'],
                                               help='Whether or not the current user has unread emails.')
        unread.set_defaults(func=lambda: print(f'You {int(not U.is_unread()) * "do not"} currently have unread messages!'))
        check_mail = subparsers.add_parser('latestmail', aliases=['latestmessages', 'latest-mail'],
                                               help='Checks the specified number of messages the user has in the current mailbox.')
        check_mail.add_argument('-size', default=10, help='Number of messages to check', type=int, required=False)
        check_mail.set_defaults(func=lambda: [print(U.mail_from_template(U.mail_from_id(i))) for i in U.check_mail(-1)[:0-args.size:-1]])# don't even ask
        close = subparsers.add_parser('close', aliases=['quit', 'cancel'],
                                               help='Logout of SMTP and IMAP3 server, close and overwrite all login data.')
        close.set_defaults(func=lambda: (U.close(), print('Closed server.'), parser.exit()))# don't even ask




        args = parser.parse_args(cmd.split())
        args.__dict__['func']() # run the function associated with each command
    except BaseException as e:
        if len(set(str(e))) == 0:
            parser.exit()
        else:
            print('Error: ', e)
