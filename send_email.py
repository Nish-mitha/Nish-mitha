# Module to be imported
from bs4 import BeautifulSoup
import requests as req
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl
import os


# Variable initialization
notify_users = {}
current_date = (datetime.datetime.now()).strftime("%B %d, %Y")
git_hub_users = os.environ.get('GIT_HUB_USERS')
port = 465
smtp_server = "smtp.gmail.com"
sender = os.environ.get('USER_EMAIL')
password = os.environ.get('USER_EMAIL')

# check if there is a contribution made today
for user_name, user_email in git_hub_users.items():
    # GitHub APIs
    user_contributions = req.get(f"https://github.com/users/{user_name}/contributions")
    data = BeautifulSoup(user_contributions.text, 'lxml')
    for tag in data.find_all('rect'):
        if current_date in tag.text and "No" in tag.text:
            notify_users[user_name] = user_email

#Send email to the user who has not contributed
for user_name, user_email in notify_users.items():
    user_information = req.get(f"https://api.github.com/users/{user_name}")
    name = (user_information.json())["name"]

    message = MIMEMultipart('alternative')
    message['From'] = f"""GitHub {sender}"""
    message['To'] = user_email
    message['Subject'] = "Reminder: Keep Up the Daily Streak! 🔥"
    html = """\
        <html>
        <head></head>
        <body>
            <p>Hey {{name}},</p>
            <p>I just wanted to remind you to keep up your daily streak on Github! 🔥</p>
            <br>
            <p>
                <img src="header.gif" alt="Anurag's GitHub stats"/>
            </p>
            <br>
            <p>
            I know that staying consistent can be hard, but it's an important part of keeping your coding skills sharp.<br>
            Every day that you commit to your project counts! </p>
            <p>
            I hope this reminder helps and I wish you the best of luck in continuing your daily streak.
            </p>
            <p>
            Kind regards,
            <br>
            Coding Buddy
            </p>
        </body>
        </html>
        """
    html_message = html.replace('{{name}}',name).replace('{{user_name}}', user_name)
    body = MIMEText(html_message, 'html')
    message.attach(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender,password)
        server.sendmail(sender,user_email,message.as_string())