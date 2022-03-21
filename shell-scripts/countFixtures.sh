#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/countFixtures_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

conda activate scraper
python /home/nico/api-football/countFixtures.py
conda deactivate

rm $Lockfile
