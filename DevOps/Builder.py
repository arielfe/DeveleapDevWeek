import subprocess
import os
import sys

repo_url = "git@github.com:arielfe/DeveleapDevWeek.git"

# usage + exit func
def usage(err=""):
    if err:
        print(f"Error: {err}")

    print("Usage: write a proper usage")
    sys.exit(1)


def main(commit, email, key):
    # need to use the key for the pull form github, for now its public so no use
    try:
        # Clone the repo if not already cloned
        repo_dir = os.path.basename(repo_url).replace(".git", "")

        if not os.path.isdir(repo_dir):
            print(f"Cloning repository from {repo_url}...")
            subprocess.run(["git", "clone", repo_url], check=True)

        # Change to the repo directory
        os.chdir(repo_dir)

        # Checkout and pull the specified commit
        subprocess.run(["git", "checkout", commit], check=True)
        subprocess.run(["git", "pull", "origin", commit], check=True)

        # Change to the directory where docker-compose.yml is located
        docker_compose_dir = os.path.join(os.getcwd(), "DevOps")

        if not os.path.isfile(os.path.join(docker_compose_dir, "docker-compose.yml")):
            usage(f"docker-compose.yml not found in {docker_compose_dir}")

        os.chdir(docker_compose_dir)

        # Run docker-compose with environment variables
        subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            env=dict(os.environ, COMMIT=commit, EMAIL=email, KEY=key),
            check=True
        )
        

        print("Pipeline completed successfully")
    
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
