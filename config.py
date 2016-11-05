import os

basedir = os.path.abspath(os.path.dirname(__file__))

# A list containing all DH22 temp/humidity sensors
# if you add others, you need to set them up in __init__.py
DHT22 = [ #(pin number, 'name')
    (15, 'internal'),
    (14,'external')
]

# a list containing all relays.  The names must be 'lights' and 'fans'
RELAYS = [ # (pin number, 'name')
    (19, 'lights'),
    (13, 'fans')
]

SETTINGS_URL = 'http://ec2-54-244-205-179.us-west-2.compute.amazonaws.com/get_settings/'

SETTINGS_JSON = os.path.join(basedir,'settings.json')

# this will be unique to each barrel.
BARREL_ID = 2

# able to toggle camera on/off
CAMERA = True