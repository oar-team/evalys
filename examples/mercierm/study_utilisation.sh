#!/usr/bin/env bash
#
# Evalys need to be installed:
# See https://github.com/oar-team/evalys
set -e

if [ ! -f traces.list ]
then
  # get list of logs
  wget -O traces.list http://www.cs.huji.ac.il/labs/parallel/workload/logs-list

  mkdir swf_files && pushd swf_files
  # get logs
  wget -i traces.list

  # unzip
  gunzip *.gz
  popd
fi

python3 compute_utilisation.py
