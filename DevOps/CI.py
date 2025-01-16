# this will be our CI app

# import relevant libs
from flask import Flask, request, abort, jsonify
import hmac
import hashlib
import os
import subprocess

app = Flask(__name__)

# SECRET= # whatever key

# # check signiture
# def verify_signature(data, signature):
#     computed_signature = 'sha256=' + hmac.new(SECRET.encode(), data, hashlib.sha256).hexdigest()
#     return hmac.compare_digest(computed_signature, signature)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    
    # Extract branch information
    ref = payload.get('ref', '')  # e.g., "refs/heads/main"
    branch_name = ref.split('/')[-1] if 'refs/heads/' in ref else None
    
    # Extract pusher email
    pusher_email = payload.get('pusher', {}).get('email', None)
    
    # Check if the push includes a Dockerfile
    commits = payload.get('commits', [])
    dockerfile_found = False

    for commit in commits:
        # Check for Dockerfile in the added or modified files
        added_files = commit.get('added', [])
        modified_files = commit.get('modified', [])
        if 'Dockerfile' in added_files or 'Dockerfile' in modified_files:
            dockerfile_found = True
            break

    if dockerfile_found:
        try:
            # Docker build command
            image_name = f"webhook-image:{branch_name}"
            build_command = [
                "docker", "build", "-t", image_name, "-f", "./Dockerfile", "."
            ]
            print(f"Building Docker image: {image_name}")
            subprocess.run(build_command, check=True)
            print("Docker image built successfully.")
            return jsonify({
                "message": "Webhook processed successfully",
                "branch_name": branch_name,
                "pusher_email": pusher_email,
                "docker_image": image_name
            }), 200
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image: {e}")
            return jsonify({"error": "Failed to build Docker image"}), 500
    else:
        return jsonify({"error": "No Dockerfile found in the push"}), 400

    # # checking for signature in headers
    # signature = request.headers.get('X-Hub-Signature-256')
    # if not signature:
    #     abort(403, 'Signature missing')
    # # check if signiture is valid
    # if not verify_signature(request.data, signature):
    #     abort(403, 'Invalid signature')
    # # take action
    # event = request.headers.get('X-GitHub-Event')
    # if event == 'push': # handling pushes
    #     try: # build image and run container
    #         # do the checks and return result
    # elif event == 'pull request' : # handling pull requests
    #     try: # build image and run container
    #         # do the checks and return result
    # else:
    #     return f"Event '{event}' not handled", 200
    # # send result to dev
# print(f'{pusher_email} is pusing into {branch_name}')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)