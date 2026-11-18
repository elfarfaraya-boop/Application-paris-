#!/bin/bash
cd "$(dirname "$0")"
trap 'kill 0' EXIT

(bash launch.sh >> ../log/data_pipeline.log 2>&1) &
(cd ../webapp/bin; bash launch.sh 2>&1 | tee -a ../../log/webapp.log)
