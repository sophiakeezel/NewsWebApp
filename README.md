# COP4521_SDK20

# Flask News Application in Python

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thank you to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Application Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Program Structure

COP4521_SDK20
.
├── cronjob.py: script to update hacker news items that runs every hour 
├── make_admin.py: make a user an admin by username
├── run.py: run flask application
├── requirements.txt: libraries used to run application
├── venv: virtual environment folder
    ├── bin
    ├── include
    ├── lib
    ├── pyvenv.cfg
├── app
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-311.pyc
    │   ├── hn_integration.cpython-311.pyc
    │   ├── models.cpython-311.pyc
    │   └── routes.cpython-311.pyc
    ├── hn_integration.py
    ├── models.py
    ├── routes.py
    ├── static
    │   └── main.css
    └── templates
        ├── admin.html
        ├── layout.html
        ├── newsfeed.html
        └── profile.html

## Code Execution

1) activate virtual environment in the terminal using the command "source /venv/bin/activate"
2) run the cronjob.py script using "python3 cronjob.py"
3) run the flask application with "python3 run.py"
4) to make a user an admin run make_admin.py using "python3 make_admin.py" and enter users email when prompted. Maker sure to complete this step after already logging in. 

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Author and acknowledgment

Sophia Keezel - sophkeezel@gmail.com

## License
For open source projects, say how it is licensed.

