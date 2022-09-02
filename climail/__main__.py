import argparse
import getpass

from . import classes as j
import colorama

my_parser = argparse.ArgumentParser(description="A CLI email client.", prog="CLImail")
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
my_parser.add_argument(
    "-smtp_server",
    metavar="smtp_server",
    type=str,
    help="The smtp server to sign in with, i.e gmail.com or outlook.com",
    default="smtp.gmail.com",
    required=False,
)
my_parser.add_argument(
    "-imap_server",
    metavar="imap_server",
    type=str,
    help="The imap server to sign in with, i.e gmail.com or outlook.com",
    default="imap.gmail.com",
    required=False,
)
my_parser.add_argument(
    "-smtp_port",
    metavar="smtp_port",
    type=int,
    help="The port to sign into the SMTP server with, is defaulted to 465",
    default=465,
    required=False,
)
my_parser.add_argument(
    "-imap_port",
    metavar="imap_port",
    type=int,
    help="The port to sign into the IMAP4 server with, is defaulted to 993",
    default=993,
    required=False,
)

# Execute the parse_args() method
args = my_parser.parse_args()
password = getpass.getpass("Password (pasting is not supported): ")
user = input("Email: ")
U = j.User(
    password=password,
    user=user,
    smtp_server=args.smtp_server,
    imap_port=args.imap_port,
    smtp_port=args.smtp_port,
    imap_server=args.imap_server,
)  # login
print("Logged in as", user)
while True:
    try:
        colorama.init(True)
        """
        BE WARNED: this is very ugly - I probably wrote this code while drunk because I have no clue how I did it.
        (I know i can use click but i don't wanna)
        """
        parser = argparse.ArgumentParser(
            description="A CLI email client.", prog="CLImail"
        )
        cmd = input("\033[38;2;0;120;255m$ CLImail\033[0m ")
        subparsers = parser.add_subparsers()
        help = subparsers.add_parser("help", help="Shows this message.")
        help.set_defaults(func=parser.print_help)
        selectmail = subparsers.add_parser(
            "selectmailbox",
            aliases=["select_mailbox", "select"],
            help='Selects a mailbox. \n NOTE: all mailboxes can be found with the "lmb" command.',
        )
        selectmail.add_argument(
            "mailbox", help="The mailbox to select.", nargs="*"
        )
        selectmail.add_argument(
            "--readonly", required=False, type=bool, default=False, const=True, nargs='?'
        )
        selectmail.set_defaults(
            func=lambda: U.select_mailbox(" ".join(args.mailbox), args.readonly)
        )
        cancelmailbox = subparsers.add_parser(
            "unselect",
            aliases=["unselect_mailbox", "cancel_mailbox"],
            help="Unselects the current mailbox.",
        )
        cancelmailbox.set_defaults(func=lambda: U.unselect_mailbox())
        list_mailboxes = subparsers.add_parser(
            "listmailboxes",
            aliases=["lmb", "mailboxes"],
            help="Lists all of the mail boxes the current user has.",
        )
        list_mailboxes.set_defaults(func=lambda: print(U.list_mailboxes()))
        sendmail = subparsers.add_parser(
            "sendmail", aliases=["send", "sendmessage"], help="Sends a message."
        )
        sendmail.add_argument(
            "-reciever", help="The address to mail.", required=True, type=str
        )
        sendmail.add_argument(
            "-content",
            help="Body of the message.",
            required=False,
            nargs="*",
            type=str,
            default=["None"],
        )
        sendmail.add_argument(
            "-subject",
            help="The subject",
            required=False,
            nargs="*",
            type=str,
            default=["None"],
        )
        sendmail.add_argument(
            "-cc",
            help="Carbon copy - addresses to send the mail to as well, seperated by spaces.",
            required=False,
            type=str,
            default=None,
            nargs="*",
        )
        sendmail.add_argument(
            "-to_attach",
            help="List of filenames/fps to attach to the mail, seperated by spaces.",
            required=False,
            type=str,
            nargs="*",
        )
        sendmail.set_defaults(
            func=lambda: (
                U.sendmail(
                    args.reciever,
                    " ".join(args.content),
                    " ".join(args.subject),
                    args.cc,
                    args.to_attach,
                ),
                print("Email sent successfully to", args.reciever + "!"),
            )
        )
        unread = subparsers.add_parser(
            "unread",
            aliases=["unreads"],
            help="Whether or not the current user has unread emails.",
        )
        unread.set_defaults(
            func=lambda: print(
                f'You {int(not U.is_unread()) * "do not"} currently have unread messages!'
            )
        )
        check_mail = subparsers.add_parser(
            "checkmail",
            aliases=["checkmessages", "check_mail", "check_messages"],
            help="Checks the specified number of messages the user has in the current mailbox.",
        )
        check_mail.add_argument(
            "size",
            help="Number of messages to check",
            type=int,
        )
        check_mail.add_argument("--save", required=False, type=bool, default=False, const=True, nargs='?')
        check_mail.add_argument("-path", default=r"\tmp", required=False, type=str)
        check_mail.set_defaults(
            func=lambda: list(
                map(
                    lambda m: (
                        print(U.mail_from_template(U.mail_from_id(m))),
                        [
                            print(
                                colorama.Fore.GREEN
                                + (i.rsplit("\\")[-1] + " was saved at " + i + "!")
                            )
                            for i in U.save_attachments(U.mail_from_id(m), args.path)
                        ]
                        if args.save
                        else None,
                    ),
                    U.mail_ids_as_str(args.size),
                )
            )
        )  # don't even ask
        current = subparsers.add_parser(
            "current",
            aliases=["current_mailbox", "current_mail"],
            help="The current mailbox selected.",
        )
        current.set_defaults(func=lambda: print(U.current_mailbox))
        close = subparsers.add_parser(
            "close",
            aliases=["quit", "cancel"],
            help="Logout of SMTP and IMAP4 server, close and overwrite all login data.",
        )
        close.set_defaults(func=lambda: (U.close(), parser.exit()))
        search = subparsers.add_parser(
            "search",
            aliases=["searchmail", "searchmessages"],
            help="Takes in a string and criteria, and returns messages that match.",
        )
        search.add_argument(
            "-string", required=False, default=None, type=str, nargs="*"
        )
        search.add_argument(
            "-criteria", required=False, nargs="*", default=["(UNSEEN)"], type=str
        )
        search.add_argument("-size", required=False, default=10, type=int)
        search.set_defaults(
            func=lambda: [
                print(U.mail_from_template(U.mail_from_id(i)))
                for i in U.search(
                    args.string if args.string is None else " ".join(args.string),
                    " ".join(args.criteria),
                    size=args.size,
                )
            ]
        )
        subscribe = subparsers.add_parser("subscribe", help="Subscribes to a mailbox.")
        subscribe.add_argument("mailbox", type=str)
        subscribe.set_defaults(func=lambda: U.subscribe(args.mailbox))
        unsubscribe = subparsers.add_parser(
            "unsubscribe", help="Unsubscribes TO a mailbox."
        )
        unsubscribe.add_argument("mailbox", type=str)
        unsubscribe.set_defaults(func=lambda: U.unsubscribe(args.mailbox))
        rename = subparsers.add_parser("rename", aliases=["renamemailbox", "renamebox"])
        rename.add_argument(
            "-old",
            required=True,
            type=str,
        )
        rename.add_argument(
            "-new",
            required=True,
            type=str,
        )
        rename.set_defaults(
            func=lambda: (
                U.rename_mailbox(args.old_mailbox, args.new_mailbox),
                print(f"Renamed mailbox {args.old_mailbox} to {args.new_mailbox}."),
            )
        )
        checksingmail = subparsers.add_parser(
            "mail", aliases=["message"], help="Returns the mail content from ID passed."
        )
        checksingmail.add_argument("id", type=int)
        checksingmail.set_defaults(
            func=lambda: print(U.mail_from_template(U.mail_from_id(args.id)))
        )
        getmail = subparsers.add_parser(
            "getids",
            aliases=["get_ids", "get_mail_ids"],
            help="Gets a specified amount of latest mail ids from the current mailbox.",
        )
        getmail.add_argument("size", type=int)
        getmail.set_defaults(func=lambda: print(*U.mail_ids_as_str(args.size)))
        crtmailbox = subparsers.add_parser(
            "new_mailbox", aliases=["newmailbox", "new_mail_box"]
        )
        crtmailbox.add_argument(
            "-name",
            required=True,
            type=str,
        )
        crtmailbox.set_defaults(func=lambda: U.create_mailbox(args.name))
        delmailbox = subparsers.add_parser(
            "delete_mailbox", aliases=["removemailbox", "delete_mail_box"]
        )
        delmailbox.add_argument(
            "-name",
            required=True,
            type=str,
        )
        delmailbox.set_defaults(func=lambda: U.delete_mailbox(args.name))
        delete_mail = subparsers.add_parser(
            "delete_mail",
            aliases=["deletemail", "del_mail"],
            help="Moves number of messages specified to trash.",
        )
        delete_mail.add_argument("size", type=int)
        delete_mail.set_defaults(func=lambda: U.delete_mail(args.size))
        delete_ids = subparsers.add_parser(
            "delete_mail_ids",
            aliases=["deletemailids", "dmi", "del_mail_ids"],
            help="Moves mail ID's specified to trash.",
        )
        delete_ids.add_argument("ids", type=str, nargs="*")
        delete_ids.set_defaults(func=lambda: U.delete_mail_ids(args.ids))
        clear = subparsers.add_parser(
            "clear",
            aliases=["clear_trash", "clear_recycling", "clear_garbage"],
            help="Permanently deletes all messages in the trash.",
        )
        clear.set_defaults(
            func=lambda: U.clear()
            if input(
                "Are you sure you want to delete all messages in the trash? (y/n) "
            ).lower()
            == "y"
            else print("Cancelled.")
        )
        refresh = subparsers.add_parser(
            "refresh",
            aliases=["restart", "reset", "reload"],
            help="Refreshes the current mailbox.",
        )

        refresh.set_defaults(func=lambda: U.refresh())
        contacts = subparsers.add_parser(
            "contacts",
            aliases=["get_contacts", "fetch_contacts"],
            help="Returns a tuple of most recent contacts in the current mailbox.",
        )
        contacts.add_argument("-size", required=False, default=10, type=int)
        contacts.set_defaults(func=lambda: print(U.contacts(args.size)))
        recon = subparsers.add_parser(
            "reconnect", help="Reconnects to the SMTP and IMAP4 servers."
        )
        recon.set_defaults(func=lambda: U.reconnect())
        save = subparsers.add_parser(
            "save",
            aliases=["save_attachments", "save_files", "savefiles", "sf"],
            help="Saves all the attachments from an email to directory specified.",
        )
        save.add_argument("-path", type=str, default=r"/tmp", required=False)
        save.add_argument("-id", type=int, required=True)
        save.set_defaults(
            func=lambda: print(
                *map(
                    (
                        lambda x, y="\\": colorama.Fore.GREEN
                        + f"{x.split(y)[-1]} was saved at {x}!"
                    ),
                    U.save_attachments(U.mail_from_id(args.id), args.path),
                ),
                sep="\n",
            )
        )

        args = parser.parse_args(cmd.split())
        # run the function associated with each command
        args.__dict__["func"]()
    except BaseException as e:
        if len(str(e)) < 1 or str(e) == "0":
            if "y" in input("Do you want to quit? (y/n): ").lower():
                parser.exit()
            else:
                continue
        print("Error: ", e)
