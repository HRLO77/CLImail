import argparse
import sys
import climail
import getpass

my_parser = argparse.ArgumentParser(
    description='A CLI email client.', prog='CLImail')
# Add the arguments
# my_parser.add_argument('-email',
#                        metavar='email',
#                        type=str,
#                        help='The email to sign in as.',
#                        required=True)
# my_parser.add_argument('-password',
#                        metavar='password',
#                        type=str,
#                        help='The password to sign in to the email with.',
#                        required=True)
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
password = getpass.getpass('Password (pasting is not supported): ')
user = input('Email: ')
try:
    U = climail.User(password=password, user=user, server=args.server,
                     imap_port=args.imap_port, smtp_port=args.smtp_port)  # login
except Exception as e:
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
        parser = argparse.ArgumentParser(
            description='A CLI email client.', prog='CLImail')
        cmd = input('>>>')
        subparsers = parser.add_subparsers()
        help = subparsers.add_parser('help',
                                     help='Shows this message.')
        help.set_defaults(func=lambda: parser.print_help())
        selectmail = subparsers.add_parser('selectmailbox', aliases=['select_mailbox', 'select'],
                                           help='Selects a mailbox. \n NOTE: all mailboxes can be found with the "lmb" command.')
        selectmail.add_argument('-mailbox', required=True,
                                help='The mailbox to select.', nargs='*')
        selectmail.add_argument('-readonly', required=False,
                                help='Readonly mode or not.', type=bool, default=False)
        selectmail.set_defaults(
            func=lambda: U.select_mailbox(" ".join(args.mailbox), args.readonly))
        cancelmailbox = subparsers.add_parser('unselect', aliases=['unselect_mailbox', 'cancel_mailbox'],
                                              help='Unselects the current mailbox.')
        cancelmailbox.set_defaults(func=lambda: U.unselect_mailbox())
        list_mailboxes = subparsers.add_parser('listmailboxes', aliases=['lmb', 'mailboxes'],
                                               help='Lists all of the mail boxes the current user has.')
        list_mailboxes.set_defaults(func=lambda: print(U.list_mailboxes()))
        sendmail = subparsers.add_parser('sendmail', aliases=['send', 'sendmessage'],
                                         help='Sends a message.')
        sendmail.add_argument(
            '-reciever', help='The address to mail.', required=True, type=str)
        sendmail.add_argument(
            '-content', help='Body of the message.', required=False, nargs='*', type=str, default=['None'])
        sendmail.add_argument('-subject', help='The subject',
                              required=False, nargs='*', type=str, default=['None'])
        sendmail.add_argument('-cc', help='Carbon copy - addresses to send the mail to as well, seperated by spaces.',
                              required=False, type=str, default=None, nargs='*')
        sendmail.add_argument(
            '-to_attach', help='List of filenames/fps to attach to the mail, seperated by spaces.', required=False, type=str, nargs="*")
        sendmail.set_defaults(func=lambda: (U.sendmail(args.reciever, " ".join(args.content), " ".join(args.subject), args.cc, args.to_attach),
                                            print('Email sent successfully to', args.reciever+'!')))
        unread = subparsers.add_parser('unread', aliases=['unreads'],
                                       help='Whether or not the current user has unread emails.')
        unread.set_defaults(func=lambda: print(
            f'You {int(not U.is_unread()) * "do not"} currently have unread messages!'))
        check_mail = subparsers.add_parser('latestmail', aliases=['latestmessages', 'latest_mail', 'latest'],
                                           help='Checks the specified number of messages the user has in the current mailbox.')
        check_mail.add_argument(
            '-size', default=10, help='Number of messages to check', type=int, required=False)
        check_mail.set_defaults(func=lambda: [print(U.mail_from_template(
            U.mail_from_id(i))) for i in U.check_mail(-1)[:0-(args.size+1):-1]])  # don't even ask
        close = subparsers.add_parser('close', aliases=['quit', 'cancel'],
                                      help='Logout of SMTP and IMAP3 server, close and overwrite all login data.')
        close.set_defaults(func=lambda: (U.close(), print(
            'Closed server.'), parser.exit()))  # don't even ask
        search = subparsers.add_parser('search', aliases=[
            'searchmail', 'searchmessages'], help='Takes in a string and criteria, and returns messages that match.')
        search.add_argument('-string', required=False,
                            default=None, type=str, nargs='*')
        search.add_argument('-criteria', required=False,
                            nargs='*', default=['(UNSEEN)'], type=str)
        search.add_argument('-size', required=False, default=10, type=int)
        search.set_defaults(func=lambda: [print(U.mail_from_template(
            U.mail_from_id(i))) for i in U.search(args.string if args.string is None else " ".join(args.string), " ".join(args.criteria), size=args.size)])
        subscribe = subparsers.add_parser(
            'subscribe', help='Subscribes to a mailbox.')
        subscribe.add_argument('-mailbox', required=True, type=str)
        subscribe.set_defaults(func=lambda: U.subscribe(args.mailbox))
        unsubscribe = subparsers.add_parser(
            'unsubscribe', help='Unsubscribes TO a mailbox.')
        unsubscribe.add_argument('-mailbox', required=True, type=str)
        unsubscribe.set_defaults(func=lambda: U.unsubscribe(args.mailbox))
        rename = subparsers.add_parser(
            'rename', aliases=['renamemailbox', 'renamebox'])
        rename.add_argument('-old_mailbox', required=True, type=str,)
        rename.add_argument('-new_mailbox', required=True, type=str,)
        rename.set_defaults(func=lambda: (U.rename_mailbox(args.old_mailbox, args.new_mailbox), print(
            f'Renamed mailbox {args.old_mailbox} to {args.new_mailbox}.')))
        checksingmail = subparsers.add_parser(
            'checkmail', aliases=['checkmessages', 'check_mail'])
        checksingmail.add_argument('-id', required=True, type=int)
        checksingmail.set_defaults(func=lambda: print(
            U.mail_from_template(U.mail_from_id(args.id))))
        crtmailbox = subparsers.add_parser(
            'new_mailbox', aliases=['newmailbox', 'new_mail_box'])
        crtmailbox.add_argument('-name', required=True, type=str,)
        crtmailbox.set_defaults(func=lambda: U.create_mailbox(args.name))
        delmailbox = subparsers.add_parser('delete_mailbox', aliases=[
            'removemailbox', 'delete_mail_box'])
        delmailbox.add_argument('-name', required=True, type=str,)
        delmailbox.set_defaults(func=lambda: U.delete_mailbox(args.name))

        args = parser.parse_args(cmd.split())
        # run the function associated with each command
        args.__dict__['func']()
    except Exception as e:
        if len(set(str(e))) == 0:
            parser.exit()
        else:
            print('Error: ', e)
