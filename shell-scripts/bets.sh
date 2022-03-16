#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/bets_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

conda activate scraper
python /home/nico/api-football/bets.py
conda deactivate

rm $Lockfile
