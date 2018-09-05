#!/usr/bin/env bash

#install deps
pip install -r requirements.txt

#populate db
echo "Note: Datadog inventory can take a few minutes."
python ec2_inventory.py

#start flask app
python app.py

#load browser
open http://0.0.0.0:5000