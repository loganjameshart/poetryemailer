#! /usr/bin/python3

"""Scrapes the Poetry Foundation's daily poem page and sends as an email."""

import os
import requests
import smtplib
import datetime
from bs4 import BeautifulSoup

# change working directory to file location so crontab job works

os.chdir("")

POEM_COUNTER = open("poemcounter.txt", "r+")
POEM_NUMBER = int(POEM_COUNTER.read())
DATE = datetime.datetime.today()
USERNAME = ""
APPKEY = ""
EMAIL_LINK = "smtp.gmail.com"
PORT = 587
RECIPIENT = ""
POETRY_LINK = f"https://www.poetryfoundation.org/poems/{str(POEM_NUMBER)}"


def get_poem(poem_link: str) -> str:
    """Takes a link to Poetry Foundation's website and returns the text of the daily poem."""
    r = requests.get(poem_link)
    soup = BeautifulSoup(r.text, "html.parser")
    poem_text = soup.find("div", class_="c-feature").text
    return poem_text


poem = get_poem(POETRY_LINK)

message = f"From: {USERNAME}\r\nTo: {RECIPIENT}\r\nSubject: Poem of the Day {DATE}\r\n{poem}\r\n".encode(
    "utf-8"
)

with smtplib.SMTP(EMAIL_LINK, PORT) as smtp_connection:
    smtp_connection.ehlo()
    smtp_connection.starttls()
    try:
        smtp_connection.login(USERNAME, APPKEY)
        smtp_connection.ehlo()
        smtp_connection.sendmail(USERNAME, RECIPIENT, message)
    except Exception as e:
        error_log = open("emailerrorlog.txt", "a")
        error_log.write(f"\nCouldn't send email on {DATE}.Error is as follows:\n{e}\n")
        print("Couldn't send. See error log for more details.")

# add 1 to poem counter file

POEM_NUMBER = POEM_NUMBER + 1
POEM_COUNTER.seek(0)
POEM_COUNTER.truncate()
POEM_COUNTER.write(str(POEM_NUMBER))
POEM_COUNTER.close()
