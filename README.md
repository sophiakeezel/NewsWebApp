# COP4521_SDK20

# Flask News Application in Python

## Description

A Python Flask Web Application that displays news from the Hacker News API to logged in Users. Allowing news post interactions such as likes, dislikes, comments, and admin access to a designated user. Users must be authenticated with the Auth0 authenticatiopn platform, and able to log out using the same platform.  

## Author
Sophia Keezel - SDK20

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configs](#configs)
- [Testing](#testing)

## Features

- Log In/Sign Up/Log Out
    - Auth0 user authentication displayed when app is first run
    - Log Out tab is displayed when a user is logged in
- Profile Page
    - Page displays user profile including name and email
    - Page displays users liked news posts
- Home Page
    - newsfeed.html and layout.html
    - displays news from Hacker News API
    - Like/Dislike buttons
    - Comment section for users to make/view commments
- Admin View
    - run "python3 make_admin.py" and enter the user email
    - admin tab will pop up on the right side when user is logged in as an admin
    - allows user to view liked/disliked news posts
    - allows user to edit and delete news post
    - allows user to view which user have liked/disliked posts

## Installation

1) Activate server using Linode
    - got to https://linode.com
    - create an account and a Linode using Ubuntu 22.04 LTS
    - ssh into server using root@<ip_address>
    - add user using adduser <username>
    - add user to sudo group using adduser <username> sudo
    - ssh into user@<ip_address>
3) clone GitLab URL "https://gitlab.com/sophiakeezel1/COP4521_SDK20.git" in home directory
5) install pip using "sudo apt install python3-pip"
6) install venv using "sudo apt install python3-venv"
7) create a virtual environment in project directory using "python3 -m venv COP4521_SDK20/venv"
8) activate venv using "source venv/bin/activate"
9) once venv is active, install dependencies using "pip install -r requirements.txt"
10) install nginx using "sudo apt install nginx"
11) install gunicorn using "pip install gunicorn"
12) remove default nginx file using "sudo rm /etc/nginx/sites-enabled/default"
13) create /etc/nginx/sites-enabled/flasknews (see configs)
14) navigate to the project directory and run gunicorn using "gunicorn -w run:app" to test
15) install aupervisor with "sudo apt install supervisor"
16) create /etc/supervisor/conf.d/flasknews.conf (see configs)
17) make directory flasknews "sudo mkdir -p /var/log/flasknews"
18) make supervisor files using "sudo touch /var/log/flasknews/flasknews.err.log" and "sudo touch /var/log/flasknews/flasknews.out.log"
19) restart supervisor using "sudo supervisorctl reload"
20) activate cronjob for cronjob.py using "crontab -e" (see configs)

## Testing

To run tests, first activate virtual environment using "source venv/bin/activate" then run "python -m unittest discover" to run tests on test_cronjob.py, test_models.py, test_routes.py

Test Results:

......
----------------------------------------------------------------------
Ran 6 tests in 0.106s

OK
