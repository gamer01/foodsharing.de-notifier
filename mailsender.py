from configparser import ConfigParser
from datetime import date
from email.message import Message
from operator import itemgetter
from smtplib import SMTP

conf = ConfigParser()
conf.read("credencials.conf")


class MailSender:
    def __init__(self, host, usr, pwd, sender):
        self.host = host
        self.usr = usr
        self.pwd = pwd
        self.sender = sender

    def __enter__(self):
        self.smtp = SMTP(host=self.host)
        self.smtp.starttls()
        self.smtp.login(self.usr, self.pwd)

    def sendmail(self, email, body):
        msg = Message()
        msg["subject"] = "foodsharing.de unbelegte Abholungen (Stand: {})".format(
            date.today().strftime("%d.%m.%Y"))
        msg["from"] = self.sender
        msg["to"] = email
        msg.set_payload(body, charset="utf-8")
        self.smtp.send_message(msg, self.sender, email)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtp.quit()

    @staticmethod
    def createinstance_from_conf():
        host, usr, pwd, sender = itemgetter("smtp_server", "smtp_username", "pwd", "sender_email")(conf["email"])
        return MailSender(host, usr, pwd, sender)
