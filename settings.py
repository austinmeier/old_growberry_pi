import json
import requests
from datetime import datetime, timedelta


class Settings(object):
    """class to hold all settings. Can get/update settings. Returns settings in correct object way"""
    def __init__(self,base_url,file_loc, grow_id):
        self.file_loc = file_loc
        self.grow_id = str(grow_id)
        self.url = base_url + self.grow_id
        self.settings = {}
        self.online = False
        self.startdate = None
        #self.sunrise = None
        self.daylength = None
        self.pic_dir = None
        self.settemp = None


    def update(self):
        try:
            # if connected to the internet, request settings
            r = requests.get(self.url)
            settings_json = r.json()   #json.loads(r.text)
            # set attributes 'online' and 'error'
            settings_json['online'] = True
            settings_json['error'] = False
            with open(self.file_loc,'w') as f:
                json.dump(settings_json,f)
        except Exception,e:
            error = {'online':False, 'error':e}
            self.settings.update(error)
        finally:
            with open(self.file_loc, 'r') as infile:
                self.settings.update(json.load(infile))
                self.startdate = datetime.strptime(self.settings.get('startdate', '042016'),'%m%d%y')
                self.sunrise = datetime.strptime(self.settings['sunrise'],'%H%M')
                self.daylength = timedelta(hours=float(self.settings['daylength']))
                self.pic_dir = self.settings['pic_dir']
                self.settemp = self.settings['settemp']

if __name__ == '__main__':
    test_grow_id = 2
    test_url = 'http://localhost:5000/get_settings/'
    test_url2 = 'http://ec2-54-244-205-179.us-west-2.compute.amazonaws.com/get_settings/'
    fl = 'settings.json'
    settings = Settings(test_url2,fl,test_grow_id)

    settings.update()
    print settings.settings
    print settings.startdate
    print settings.sunrise
    print settings.daylength