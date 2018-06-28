#!/bin/bash

cd $(dirname $0)

jenkins-jobs --conf jenkins.ini update job-generator.yaml

cat job-generator.yaml | yq -r '.[].job.name' # | awk '{print "Updated" $1}'
