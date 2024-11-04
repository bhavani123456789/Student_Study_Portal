from .common import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY=os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['studentstudyportal-prod-848a5ccf8276.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config()
}