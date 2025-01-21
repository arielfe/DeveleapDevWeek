#!/bin/bash
# read configuration file for compose file locations within the repository


# clone the git repository and checkout the right commit                                                                                                                                               
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git clone  git@github.com:arielfe/DeveleapDevWeek.git             
cd DeveleapDevWeek                                                                                                                                             
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git checkout $COMMIT                                              

# change directory to top of repository and store as reference point
REPO_ROOT=$(pwd)

. ./DevOps/config/compose_targets.sh

# execute each docker compose testing file
#cd $BILLING_TEST_COMPOSE_FOLDER
#docker compose -f $BILLING_TEST_COMPOSE_FILE up
echo $REPO_ROOT
echo $WEIGHT_TEST_COMPOSE_FOLDER
cd $REPO_ROOT
cd $WEIGHT_TEST_COMPOSE_FOLDER
pwd
echo "docker compose -f $WEIGHT_TEST_COMPOSE_FILE up"
docker compose -f $WEIGHT_TEST_COMPOSE_FILE up

# run build test script. the script will also return mail to the committer
#cd $REPO_ROOT
#cd DevOps/build_tests
#python build_test.py

# if this is main branch and tests successful, need to run deployment
#DEPLOY="NO"
#if [ $? -eq 0 && $MAIN_BRANCH -eq "YES" ]; then
#   DEPLOY="YES"
#fi

# drop all testing env 
#cd $BILLING_TEST_COMPOSE_FOLDER
#docker compose -v -f $BILLING_TEST_COMPOSE_FILE down
#cd $REPO_ROOT
#cd $WEIGHT_TEST_COMPOSE_FOLDER
#docker compose -v -f $WEIGHT_TEST_COMPOSE_FILE down
#cd $REPO_ROOT

# deploy if needded
if [[ $DEPLOY == "YES" ]]; then
   cd $BILLING_DEPLOY_COMPOSE_FOLDER
   docker compose -f  $BILLING_DEPLOY_COMPOSE_FILE up -d
   cd $REPO_ROOT
   cd $WEIGHT_DEPLOY_COMPOSE_FOLDER
   docker compose -f $WEIGHT_DEPLOY_COMPOSE_FILE -d
   cd $REPO_ROOT
   # run post deploy tests
   cd DevOps/build_tests
   #python deploy_test.py
fi

