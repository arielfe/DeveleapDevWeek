# does this container know this imports ?
import smtplib
import requests

# services api
services = {
    "weight-service": "http://weight-service:5000/health",
    "billing-service": "http://billing-service:5002/health"
}

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
        s.sendmail(email_user, "ariel.fellous@gmail.com", msg)
        s.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

# check and call email func
def check_health():
    # for each service + url
    for service_name, url in services.items():
        try:
            response = requests.get(url)

            #  on success
            if response.status_code == 200:
                msg = f"[SUCCESS] {service_name} is healthy, Status Code: {response.status_code}"
                print(msg)
                send_email(msg)

            # on failure
            else:
                msg = f"[FAILURE] {service_name} responded with Status Code: {response.status_code}"
                print(msg)
                send_email(msg)
                
        # catch request error       
        except requests.exceptions.RequestException as e:
            msg = f"[ERROR] Could not connect to {service_name}: {e}"
            print(msg)
            send_email(msg)

if __name__ == "__main__":
    check_health()
