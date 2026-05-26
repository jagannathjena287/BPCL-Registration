#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python -c "from database import init_db; init_db()"
