import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from creativecoin import app


class EmailSender:
    def __init__(self):
        self.smtp = app.config['SMTP']
        self.smtp_port = app.config['SMTP_PORT']
        self.username = app.config['SMTP_USER']
        self.password = app.config['SMTP_PASS']
        self.sender = app.config['SMTP_FROM']


    def prepare_body(self, parameters, path):
        """
        Inserts the proper text and values (defined in `parameters`) to the placeholders in the the template html provided by `path`
        
        Parameters:
        -----------
        parameters (dict): Key-value pair containing the name of the placeholder. eg. {"customer_name": "John Doe"}
        path (string): Path of the template html to be used

        Returns:
        -----------
        body (str): The html codes with parameters inserted
        """
        with open('creativecoin/templates/email/{}'.format(path)) as f:
            body = f.read()

        for k,v in parameters.items():
            body = body.replace(k,v)

        return body


    def send_mail(self, to, subject, body):
        """
        Sends the email

        Parameters:
        -----------
        to (str): email of the recepient
        subject (str): subject of the email
        body (str): html codes of the whole message

        Returns:
        boolean: True if sending is successful else False
        """      
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = to if app.config['ENV'] == "production" else "tbcmsapp@gmail.com"

            mime = MIMEText(body, "html")
            msg.attach(mime)

            s = smtplib.SMTP_SSL(host=self.smtp, port=self.smtp_port)
            s.login(self.username, self.password)
            s.sendmail(self.username, 
                to if app.config['ENV'] == "production" else "tbcmsapp@gmail.com", 
                msg.as_string())
            s.quit()
            app.logger.info("Message sent")
        except Exception as e:
            app.logger.error(e)
            return False

        return True
