#!/bin/bash
touch info.log
chmod 777 info.log
service nginx start
uwsgi --ini uwsgi.ini