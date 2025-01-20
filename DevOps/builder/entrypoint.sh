#!/bin/sh                                                                                                                                                      
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git clone  git@github.com:arielfe/DeveleapDevWeek.git             
cd DeveleapDevWeek                                                                                                                                             
GIT_SSH_COMMAND="ssh -i /conf/id_ed25519_dev -o LogLevel=quiet -o StrictHostKeyChecking=no " git checkout $COMMIT                                              
cd DevOps/compose                                                                                                                                              
docker compose up  --always-recreate-deps --abort-on-container-exit 

