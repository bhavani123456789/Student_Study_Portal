from .common import *


SECRET_KEY = 'django-insecure-r!xms*8(s%9ym&la!dr@n@n_o*l8bed3n0%kvp#e+(v&3u2si2'

DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'studentportal',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '1122'
    }
}