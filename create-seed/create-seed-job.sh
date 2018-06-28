#!/bin/bash

cd $(dirname $0)

jenkins-jobs --conf jenkins.ini update job-generator.yaml

cat job-generator.yaml | yq -r '.[].job.name' | xargs -i{} echo "*** Updated {} job ***"
