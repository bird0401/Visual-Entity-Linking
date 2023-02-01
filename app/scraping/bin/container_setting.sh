#!/bin/sh

apt update; apt -y upgrade
apt-get install vim
vim /usr/local/lib/python3.10/site-packages/fake_useragent/utils.py
# before: html = html.split('<table class="w3-table-all notranslate">')[1]
# after: html = html.split('<table class="ws-table-all notranslate">')[1]