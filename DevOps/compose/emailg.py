import smtplib
import os

email_user = os.environ("EMAIL")
email_pass = os.environ("EMAIL_PASS")
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
