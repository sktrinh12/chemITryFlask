#!/bin/bash
echo "testing!"
. /opt/conda/etc/profile.d/conda.sh
conda activate py36
# gunicorn --bind 0.0.0.0:5000 run:app
