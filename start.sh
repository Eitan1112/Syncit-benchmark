#!/bin/bash
touch info.log
chmod 777 info.log
uwsgi --ini uwsgi.ini