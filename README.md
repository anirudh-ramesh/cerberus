# Irasus Web Application

# Require Install

# 1 python3
# 2 Postgres

# Installment

- pip install python3


## Setup

The first thing to do is to clone the repository:

```
$ git clone https://github.com/dixitIms/cerberus.git
$ cd cerberus

```

Then go to Directory Myenv a virtual environment to install dependencies in and activate it:

cd mysite/myenv
source env/bin/activate

Then Move from myenv to Project Directory
    use Command cd .. 
    Eg :- work/djangoproject/cerberus/cerberus

(env)$ python manage.py runserver

And navigate to `http://127.0.0.1:8000/`. this is The Dashboard

## Walkthrough

Before you interact with the application, go to 
the Redirect URI in the Developer settings. To make it work with this
application, use the value `http://127.0.0.1:8000/login`. This is to
make sure you are redirected back to your site where the user login


use the value `http://127.0.0.1:8000/register`. This redirected back to your site where the user register
