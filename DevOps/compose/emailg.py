import smtplib
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
s.starttls()
# Authentication
s.login("ariel.fellous", "erpg dznp mofo nryi ")
# message to be sent
message = "Message_you_need_to_send"
# sending the mail
s.sendmail("devweekorange@gmail.com", "ariel.fellous@gmail.com", message)
# terminating the session
s.quit()
