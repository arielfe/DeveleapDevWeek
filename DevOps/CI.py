# this will be our CI app

# import relevant libs
from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)

SECRET= # whatever key

# check 
def verify_signature(data, signature):
    computed_signature = 'sha256=' + hmac.new(SECRET.encode(), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)
@app.route('/webhook', methods=['POST'])
def github_webhook():
    # checking for signature in headers
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        abort(403, 'Signature missing')
    # check if signiture is valid
    if not verify_signature(request.data, signature):
        abort(403, 'Invalid signature')
    # take action
    event = request.headers.get('X-GitHub-Event')
    if event == 'push': # handling pushes
        try: # build image and run container
            # do the checks and return result
    elif event == 'pull request' : # handling pull requests
        try: # build image and run container
            # do the checks and return result
    else:
        return f"Event '{event}' not handled", 200
    # send result to dev
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)