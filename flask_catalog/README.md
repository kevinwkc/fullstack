RUN
=====================
# Catalog

## Section 0: Intro
You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Section 1: Set Up Environment
vagrant up
vagrant ssh
cd /vagrant/catalog


## Section 2: Requirements
Cheetah==2.4.4
Flask==0.10.1
Flask-HTTPAuth==3.2.1
Jinja2==2.7.2
Landscape-Client==14.12
MarkupSafe==0.18
PAM==0.4.2
PyYAML==3.10
SQLAlchemy==0.8.4
SecretStorage==2.0.0
Twisted-Core==13.2.0
Twisted-Names==13.2.0
Twisted-Web==13.2.0
Werkzeug==0.9.4
apt-xapian-index==0.45
argparse==1.2.1
bleach==1.4.3
blinker==1.3
chardet==2.0.1
cloud-init==0.7.5
colorama==0.2.5
configobj==4.7.2
html5lib==0.999
httplib2==0.9.2
itsdangerous==0.22
jsonpatch==1.3
jsonpointer==1.0
keyring==3.5
launchpadlib==1.10.2
lazr.restfulclient==0.13.3
lazr.uri==1.0.3
oauth==1.0.1
oauth2client==3.0.0
passlib==1.6.5
prettytable==0.7.2
psycopg2==2.4.5
pyOpenSSL==0.13
pyasn1==0.1.9
pyasn1-modules==0.0.8
pycrypto==2.6.1
pycurl==7.19.3
pygobject==3.12.0
pyinotify==0.9.4
pyserial==2.6
python-apt==0.9.3.5ubuntu2
python-debian==0.1.21-nmu2ubuntu2
redis==2.10.5
requests==2.2.1
rsa==3.4.2
simplejson==3.3.1
six==1.10.0
ssh-import-id==3.21
urllib3==1.7.1
wadllib==1.3.2
wheel==0.24.0
wsgiref==0.1.2
zope.interface==4.0.5

## Section 3: Installation
copy the zip file

## Section 4: Set Up
rm catalog.db
python models.py
python lotsofCat.py


## Section 5: How to run
python main.py

go to http://localhost:5000

## Section 6: Usage
https://review.udacity.com/#!/rubrics/5/view