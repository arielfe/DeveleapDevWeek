from flask import Flask, request, abort, jsonify
import subprocess

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify("OK"), 200

@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    if not payload:
        abort(400, "Missing or invalid payload")

    # Extract commit ID (from the first commit) and pusher email
    commit = payload.get('commits', [{}])[0].get('id', None)
    if not commit:
        abort(400, "Commit ID not found")
    pusher_email = payload.get('pusher', {}).get('email', None)

    # Dynamically pass the variable to a new container
    command = [
        "docker", "run", "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/conf:/conf",
        "-e", f"COMMIT={commit}",
        "-e", f"EMAIL={pusher_email}",
        "build" # Image name
    ]

    # Run the command
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"status": "error", "error": result.stderr.strip()}), 500
        return jsonify({"status": "success", "output": result.stdout.strip()})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
