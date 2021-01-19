# run cron command
# !/bin/bash

echo "cron job is started"


#must be in vitualenv

while :
do
        /media/hamid/uni_com/fanaba/Dev/DVS/venv/bin/python3 /media/hamid/uni_com/fanaba/Dev/DVS/manage.py  runcrons
        echo "===================runned perfectly========================="
        sleep 2
done