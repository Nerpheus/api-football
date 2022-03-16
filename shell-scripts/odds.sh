#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/odds_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

conda activate scraper
python /home/nico/api-football/odds.py
conda deactivate

rm $Lockfile
