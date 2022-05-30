from climail import User
import email

class user(User):

    def mail_from_template(self, message: email.message.Message):
        '''
        Takes a email.message.Message object and creates a message out of a template for it. (Not sure if template is the right word.)
        '''
        string = '================== Start of Mail #{i} ====================\n'
        string += f'From:    {message.get("From")}\n'
        string += f'To:      {message.get("To")}\n'
        string += f'Cc:      {message.get("Cc")}\n'
        string += f'Bcc:     {message.get("Bcc")}\n'
        string += f'Date:    {message.get("Date")}\n'
        string += f'Subject: {message.get("Subject")}\n'
        for i in message.walk():
            if i.get_content_type() == "text/plain":
                string += i.as_string()
        string += '\ns================== End of Mail #{i} ======================\n'
        return string