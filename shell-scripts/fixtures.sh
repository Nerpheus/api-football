#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/fixtures_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

conda activate scraper
python /home/nico/api-football/fixtures.py
conda deactivate

rm $Lockfile
