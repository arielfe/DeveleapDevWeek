import smtplib
import requests
import sys
import os


# services
services = {
    "backend-weight":"http://localhost:5555/health",
    "backend-billing":"http://localhost:5000/health",
    "frontend billing":"http://localhost:8084/health"
    }

commiter = os.environ("EMAIL")

# extract email data
with open('/run/secrets/my_email', 'r') as file:
    email_user = file.read().strip()
with open('/run/secrets/my_password', 'r') as file:
    email_pass = file.read().strip()


#  email func
def send_email(msg):
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email_user, email_pass)
        s.sendmail(email_user, commiter, msg)
        s.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        return sys.exit(1)

# check and call email func
def check_health():

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
            msg = f"[ERROR] Could not connect to {service_name}: {e}"
            print(msg)
            messages += f'{msg}\n'

    # sending email on both cases
    send_email(messages)

    # exit codes for success/faliure
    if is_success:
        return sys.exit(0)
    else:
        return sys.exit(1)


if __name__ == "__main__":
    check_health()