# devops-service/app.py
from flask import Flask, request, jsonify
import subprocess
import os
import sys


# usage + exit func
def usage(err=""):
    if err:
        print(f"Error: {err}")

    print("Usage: write a proper usage")
    sys.exit(1)


def main(commit, email, key):
    # need to use the key for the pull form github, for now its public so no use
    try:
        subprocess.run(["git", "checkout", commit], check=True)
        subprocess.run(["git", "pull", "origin", commit], check=True)

        # use docker compose + passing paramaters: commit + email 
        subprocess.run([
            "docker-compose",
            "-f", "docker-compose.yml",
            "up", "-d"
            "--build-arg", f"COMMIT={commit}",
            "--build-arg", f"EMAIL={email}"
            ], check=True)

        return "Pipeline completed successfully"
    
    except subprocess.CalledProcessError as e:
        # handle error
        return usage("git or docker compose fail")


# main
if __name__ == '__main__':

    # recive exact 3 args
    if len(sys.argv) != 4:
        usage("try again, need to provide 3 args, \nCommit \nEmail \nkey")

    # extract args to variables
    commit, email, key = sys.argv[1], sys.argv[2], sys.argv[3]
    
    # call main with the args
    main(commit, email, key)
