import smtplib
import requests
import sys
import os
import time
from email.message import EmailMessage


# services
services = {
    "backend-weight":"http://127.0.0.1:8085/health",
    "backend-billing":"http://127.0.0.1:5000/health",
    "frontend billing":"http://127.0.0.1:8084/health"
    }

commiter = os.environ.get("EMAIL")

# extract email data
with open('/conf/email', 'r') as file:
    email_user = file.read().strip()
with open('/conf/emailpass', 'r') as file:
    email_pass = file.read().strip()


#  email func
def send_email(msg, subject):
    try:
        message = EmailMessage()
        message.set_content(msg)
        message["Subject"] = subject
        message["From"] = email_user
        message["To"] = commiter
        #message = 'Subject: {}\n\n{}'.format(subject, msg)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email_user, email_pass)
        #print("msg")
        #print(msg)
        #s.sendmail(email_user, commiter, msg)
        s.send_message(message)
        s.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        return sys.exit(1)

# check and call email func
def check_health():

    time.sleep(2)
    messages = '' 
    is_success= True

    # for each service + url
    for service_name, url in services.items():
        try:
            response = requests.get(url)

            #  on success
            if response.status_code == 200:
                msg = f"[SUCCESS] {service_name} is healthy, Status Code: {response.status_code}"
                print(msg)
                messages += f'{msg}\n'

            # on failure
            else:
                is_success = False
                msg = f"[FAILURE] {service_name} responded with Status Code: {response.status_code}"
                print(msg)
                messages += f'{msg}\n'
                
                
        # catch request error       
        except requests.exceptions.RequestException as e:
            is_success = False
            msg = f"[ERROR] Could not connect to {service_name}"
            print(msg)
            messages += f'{msg}\n'

    # sending email on both cases
    if is_success:
       subject = 'build success'
    else:
        subject = 'build failed'
    send_email(messages, subject)

    # exit codes for success/faliure
    if is_success:
        return sys.exit(0)
    else:
        return sys.exit(1)


if __name__ == "__main__":
    check_health()
