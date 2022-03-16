#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/leagues_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

conda activate scraper
python /home/nico/api-football/leagues.py
conda deactivate

rm $Lockfile
