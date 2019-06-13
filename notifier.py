#!/usr/bin/env python3

import json
import locale
import os.path
import socket
from configparser import ConfigParser
from datetime import date, datetime, timedelta
from logging import error, warning
from operator import itemgetter
from smtplib import SMTPAuthenticationError

import requests
from bs4 import BeautifulSoup

from mailsender import MailSender

credentials = ConfigParser()
credentials.read("credentials.conf")
conf = ConfigParser()
conf.read("general.conf")

locale.setlocale(locale.LC_ALL, conf.get("DEFAULT", "locale"))


class Termin(datetime):
    n_empty_slots = 0
    firm = ""

    def __new__(cls, dt, i, firm):
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute)

    def __init__(self, dt, i, firm):
        super().__init__()
        self.n_empty_slots = i
        self.firm = firm

    def __str__(self):
        return f"{self.strftime('%a %d.%b')}: {self.n_empty_slots} Slots bei {self.firm}"

    def has_empty(self):
        return self.n_empty_slots > 0

    def key(self):
        return self.isoformat(), self.firm

    @staticmethod
    def create_instance(soup, firm):
        dt = datetime.fromisoformat(soup.select("input")[0]["value"])
        t = Termin(dt, len(soup.select("li.empty")), firm)
        return t


def activate_session(session):
    usr, pwd = itemgetter('usr', 'pwd')(credentials["foodsharing.de"])
    data = {"email": usr, "password": pwd}
    session.post(conf.get("foodsharing.de", "host") + "api/user/login", json=data)
    return session


def get_firm(s):
    soup = BeautifulSoup(s.get(conf.get("foodsharing.de", "host") + "?page=dashboard").text, features="lxml")
    # return all hrefs on the dashboard page that link to "fsbetrieb" meaning firm
    # the complicated select picks all a tags that have no children
    # make sure that each firm is only added once
    firms = {a["href"]: a.text for a in soup.select("a:not(:has(> *))") if "page=fsbetrieb" in a["href"]}
    # now we can flip the dictionary
    return {v: k for k, v in firms.items()}


def get_events(s, firm, url):
    soup = BeautifulSoup(s.get(conf.get("foodsharing.de", "host") + url).text, features="lxml")
    termine = soup.select(".field:contains('Nächste Abholtermine') .element-wrapper")
    return [Termin.create_instance(t, firm) for t in termine]


def send_mails(data):
    maintext = "\n".join((str(t) for t in sorted(data)))
    with open("emails.txt") as f:
        mails = [line.strip() for line in f]
    with open(conf.get("DEFAULT","email_template")) as f:
        tmpl = f.read()
    body = tmpl.format(list=maintext,**{k: v for d in map(dict,dict(conf).values()) for k, v in d.items()})


    host, usr, pwd, sender = itemgetter("smtp_server", "smtp_username", "smtp_pwd", "sender_email")(
        credentials["email"])
    mailsender = MailSender(host, usr, pwd, sender)
    print(body)
    print(f"\nSending {len(mails)} Emails", end="")
    try:
        with mailsender:
            for mail in mails:
                mailsender.sendmail(mail, body)
    except SMTPAuthenticationError:
        error("EmailAuthentication Failed. No emails sent.")
    except socket.gaierror:
        warning("No network connection")
    print("\rEmails sent   ")


if __name__ == "__main__":
    data = set()

    with requests.Session() as s:
        activate_session(s)
        firms = get_firm(s)
        for title, url in firms.items():
            events = get_events(s, title, url)
            for event in events:
                if event.date() < date.today() + timedelta(days=conf.getint("DEFAULT", "lookahead_days")) and event.has_empty():
                    data.add(event)

    old_events = set()
    new_events = {t.key() for t in data}
    datafile = conf.get("DEFAULT", "datafile")
    if os.path.isfile(datafile):
        with open(datafile, "r") as f:
            # load old events and update
            old_events = set((tuple(elem) for elem in json.load(f)))
    with open(datafile, "w") as f:
        json.dump(list(new_events), f)

    if new_events - old_events:
        # a new event has been added
        send_mails(data)
