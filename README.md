Agenda:
The first script {name} connects to Zabbix via the API and retrieves the names and IP addresses of all cameras in a specific group.
  Then it downloads them to /tmp/data/{cam_name}.jpg
  
The second script {name} sends the collected data and the captured photo to Telegram

Zabbix pre-configuration:  
  Alerts → Media types — create a media type with the type script_name.
  Script parameters:
  the second parameter is {HOST.NAME},
  the third parameter is {ALERT.MESSAGE}

Python .env
    ZAB_IP=
    ZAB_USR=
    ZAB_PASSWD=
    CAMS_USR=
    CAMS_PASSWD=
    CAMS_GROUP=
    BOT_TOKEN=
    CHAT_ID=
