#!/bin/bash

#pwd

cd $(dirname $0)

#pwd
#
#ls -la

#set

if [ ! "$JENKINS_HOME" = "" ]; then
    ls -la $JENKINS_HOME
    mkdir -p $JENKINS_HOME/workspace/.jobs-builder-cache
    export XDG_CACHE_HOME="$JENKINS_HOME/workspace/.jobs-builder-cache"
fi

type jenkins-jobs >/dev/null 2>&1 || {
    echo "Install jenkins jobs builder via `pip3 install jenkins-job-builder`"
    exit -1
}


jenkins-jobs --conf jenkins.ini update job-generator.yaml || exit 2

#ls -la $XDG_CACHE_HOME

#cat job-generator.yaml | yq -r '.[].job.name' | xargs -i{} echo "*** Updated {} job ***"
