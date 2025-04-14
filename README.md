# TK-gjestenett-auto-login
Script to automatically log into TK-gjestenett - Trondheim kommunes guest wifi. If your using a private computer running Linux at work and can't log into TK-nett.

You need to create the file /etc/wifi-login.conf containing the following:

[DEFAULT]
WIFI_USERNAME=your username here
WIFI_PASSWORD=your password here

chmod 600 the file.

Add wifi-autologon.py to /usr/local/bin/
Add 97-auto-wifi-login to /etc/NetworkManager/dispatcher.d/
