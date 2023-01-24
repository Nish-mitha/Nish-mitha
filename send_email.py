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
git_hub_users = {}
git_hub_users = os.environ.get('GIT_HUB_USERS').split(',')
port = 465
smtp_server = "smtp.gmail.com"
sender = os.environ.get('USER_EMAIL')
password = os.environ.get('USER_PASSWORD')

# check if there is a contribution made today
for user in git_hub_users:
    # GitHub APIs
    user_data = user.split(':')
    user_name = user_data[0]
    user_email = user_data[1]
    user_contributions = req.get(f"https://github.com/users/{user_name}/contributions")
    data = BeautifulSoup(user_contributions.text, 'lxml')
    for tag in data.find_all('rect'):
        if current_date in tag.text and "No" in tag.text:
            user_information = req.get(f"https://api.github.com/users/{user_name}")
            name = (user_information.json())["name"]
            
            # Get the Streak Data
            streak_info = []
            user_streak_stats = req.get(f"https://github-readme-streak-stats.herokuapp.com/?user={user_name}&show_icons=true&theme=radical")
            stats = BeautifulSoup(user_streak_stats.text, 'lxml')
            for tag in stats.find_all('text'):
                data = (tag.text).strip()
                streak_info.append(data)

            # Construct Email
            message = MIMEMultipart('alternative')
            message['From'] = f"""GitHub {sender}"""
            message['To'] = user_email
            message['Subject'] = "Reminder: Keep Up the Daily Streak! 🔥"
            html = """\
                <html>
                <head>
                    <style>
                        .rect { width:494px; height:194px; background-color:#141321; border:1px solid #e4e2e2; } .line_1 { border-left: 1px solid #e4e2e2; height: 142px; position: absolute; margin-left: 165px; margin-top: 26px; } .line_2 { border-left: 1px solid #e4e2e2; height: 142px; position: absolute; margin-left: 330px; margin-top: 26px; }
                        .main_counter_1 { color: #fe428e; font-size: 28px; font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 700; font-style: normal; margin-left: 60.5px; margin-top: 52px; } .main_text_1 { color: #fe428e; font-size: 14px; font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 400; font-style: normal; margin-left: 26.5px; margin-top: -9px; } .sub_text_1 { color: rgb(169, 254, 247); font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 400; font-size: 12px; font-style: normal; margin-left: 28.5px; margin-top: -2px; }
                        .main_counter_2 { color: rgb(248, 216, 71); text-align: center; font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 700; font-size: 28px; font-style: normal; margin-top: -108px; } .main_text_2 { color: rgb(248, 216, 71); font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 700; text-align: center; font-size: 14px; font-style: normal; margin-top: -9px; } .sub_text_2 { color: rgb(169, 254, 247); font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 400; font-size: 12px; font-style: normal; text-align: center; margin-top: -2px; }
                        .main_counter_3 { color: #fe428e; font-size: 30px; font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 700; font-style: normal; margin-left: 397.5px; margin-top: -102px; } .main_text_3 { color: #fe428e; font-size: 14px; font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 400; font-style: normal; margin-left: 361.5px; margin-top: -11px; } .sub_text_3 { color: rgb(169, 254, 247); font-family: "Segoe UI", Ubuntu, sans-serif; font-weight: 400; font-size: 12px; font-style: normal; margin-left: 364.5px; margin-top: -4px; }
                    </style>
                </head>
                <body>
                    <p>Hey {{name}},</p>
                    <p>I just wanted to remind you to keep up your daily streak on Github! 🔥</p> 
                    <br>
                    <div class="rect">
                        <div class="line_1"></div>
                        <div class="line_2"></div>
                        <p class="main_counter_1">{{streak_info[0]}}</p>
                        <p class="main_text_1">Total Contributions</p>
                        <p class="sub_text_1">{{streak_info[2]}}</p>
                        <p class="main_counter_2">🔥{{streak_info[3]}}</p>
                        <p class="main_text_2">Current Streak</p>
                        <p class="sub_text_2">{{streak_info[5]}}</p>
                        <p class="main_counter_3">{{streak_info[6]}}</p>
                        <p class="main_text_3">Longest Streak</p>
                        <p class="sub_text_3">{{streak_info[8]}}</p>
                    </div>
                    <br>
                    <p>
                    I know that staying consistent can be hard, but it's an important part of keeping your coding skills sharp.Every day that you commit to your project counts! </p>
                    <p>
                    I hope this reminder helps and I wish you the best of luck in continuing your daily streak.
                    </p>
                    <p>
                    Kind regards,
                    <br>
                    Coding Buddy🔥
                    </p>
                </body>
                </html>
                """
            html_message = html.replace('{{name}}',name).replace('{{user_name}}', user_name).replace('{{streak_info[0]}}', streak_info[0]).replace('{{streak_info[2]}}', streak_info[2]).replace('{{streak_info[3]}}', streak_info[3]).replace('{{streak_info[5]}}', streak_info[5]).replace('{{streak_info[6]}}', streak_info[6]).replace('{{streak_info[8]}}', streak_info[8])
            body = MIMEText(html_message, 'html')
            message.attach(body)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender,password)
                server.sendmail(sender,user_email,message.as_string())
