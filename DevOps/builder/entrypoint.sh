#!/bin/sh

# read configuration file for compose file locations within the repository
. DevOps/config/compose_targets.sh


# clone the git repository and checkout the right commit                                                                                                                                               
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git clone  git@github.com:arielfe/DeveleapDevWeek.git             
cd DeveleapDevWeek                                                                                                                                             
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git checkout $COMMIT                                              

# change directory to top of repository and store as reference point
cd DeveleapDevWeek
REPO_ROOT=$(pwd)


# execute each docker compose testing file
cd $BILLING_TEST_COMPOSE_FOLDER
docker compose up -f $BILLING_TEST_COMPOSE_FILE
cd $REPO_ROOT
cd $WEIGHT_TEST_COMPOSE_FOLDER
docker compose up -f $WEIGHT_TEST_COMPOSE_FILE

# run build test script. the script will also return mail to the committer
cd $REPO_ROOT
cd DevOps/build_tests
python build_test.py

# if this is main branch and tests successful, need to run deployment
DEPLOY="NO"
if [ $? -eq 0 && $MAIN_BRANCH -eq "YES" ]; then
   DEPLOY="YES"
fi

# drop all testing env 
cd $BILLING_TEST_COMPOSE_FOLDER
docker compose down -v -f $BILLING_TEST_COMPOSE_FILE
cd $REPO_ROOT
cd $WEIGHT_TEST_COMPOSE_FOLDER
docker compose down -v -f $WEIGHT_TEST_COMPOSE_FILE
cd $REPO_ROOT

# deploy if needded
if [ $DEPLOY -eq "YES" ]; then
   cd $BILLING_DEPLOY_COMPOSE_FOLDER
   docker compose up -f  $BILLING_DEPLOY_COMPOSE_FILE
   cd $REPO_ROOT
   cd $WEIGHT_DEPLOY_COMPOSE_FOLDER
   docker compose up -f $WEIGHT_DEPLOY_COMPOSE_FILE
   cd $REPO_ROOT
   # run post deploy tests
   cd DevOps/build_tests
   python deploy_test.py
fi

