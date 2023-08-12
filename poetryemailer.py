#! (venv)/bin python3
"""Scrapes the Poetry Foundation's daily poem page and sends as an email."""

import os
import requests
import smtplib
from email.message import EmailMessage
import datetime
from bs4 import BeautifulSoup

# change working directory to script's path so cron job works

os.chdir("")

POEM_COUNTER = open(
    "poemcounter.txt", "r+"
)  # using open instead of context manager since the file is written to at the end of the script
POEM_NUMBER = int(POEM_COUNTER.read())
DATE = datetime.datetime.today()
SENDER = ""
APPKEY = ""
EMAIL_LINK = "smtp.gmail.com"
PORT = 587
RECIPIENT = ""
POETRY_LINK = f"https://www.poetryfoundation.org/poems/{str(POEM_NUMBER)}"


def get_poem(poem_link: str) -> str:
    """Takes a link to Poetry Foundation's website and returns the text of the daily poem."""
    r = requests.get(poem_link)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        poem_body = soup.find("div", class_="c-feature").text
        return poem_body
    else:
        error_log = open("emailerrorlog.txt", "a")
        error_log.write(f"\nCouldn't get poem. Status code is {r.status_code}.")


poem = get_poem(POETRY_LINK)

# build email message

message = EmailMessage()
message["Subject"] = f"Poem of the Day for {DATE}"
message["From"] = SENDER
message["To"] = RECIPIENT
message.set_content(poem)

with smtplib.SMTP(EMAIL_LINK, PORT) as smtp_connection:
    smtp_connection.ehlo()
    smtp_connection.starttls()
    try:
        smtp_connection.login(SENDER, APPKEY)
        smtp_connection.ehlo()
        smtp_connection.send_message(message)
    except Exception as e:
        error_log = open("emailerrorlog.txt", "a")
        error_log.write(f"\nCouldn't send email on {DATE}.Error is as follows:\n{e}\n")
        print("Couldn't send. See error log for more details.")

# add 1 to poem counter file

POEM_NUMBER = POEM_NUMBER + 1
POEM_COUNTER.seek(0)
POEM_COUNTER.write(str(POEM_NUMBER))
POEM_COUNTER.close()
