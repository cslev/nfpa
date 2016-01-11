#!/bin/bash

echo -e "Stopping NFPA and its whole process subtree"
nfpa_pid=`cat nfpa.pid`
kill -9 `pstree -p $nfpa_pid | grep -oP '(?<=\()[0-9]+(?=\))' | sort -r`
