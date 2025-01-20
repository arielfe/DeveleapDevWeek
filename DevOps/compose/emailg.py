import smtplib
import os

with open('/run/secrets/my_email', 'r') as file:
     email_user = file.read().replace('\n', '')
with open('/run/secrets/my_password', 'r') as file:
     email_pass = file.read().replace('\n', '')
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
s.starttls()
# Authentication
s.login(email_user, email_pass)
# message to be sent
message = "Message_you_need_to_send"
# sending the mail
s.sendmail(email_user, "ariel.fellous@gmail.com", message)
# terminating the session
s.quit()
