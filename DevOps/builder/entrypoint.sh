#!/bin/sh                                                                                                                                                      
DEPLOY="NO"
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git clone  git@github.com:arielfe/DeveleapDevWeek.git             
cd DeveleapDevWeek                                                                                                                                             
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git checkout $COMMIT                                              
cd DevOps/compose 
export COMPOSE_PROJECT_NAME=$COMMIT                                                                                                                                        
docker compose up  --always-recreate-deps --abort-on-container-exit --attach devops-service

if [ $? -eq 0 && $MAIN_BRANCH -eq "YES" ]; then
   DEPLOY="YES"
fi
docker compose down -v

if [ $DEPLOY -eq "YES" ]; then
	#DEPLOY CODE
fi

