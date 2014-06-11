'''
Created on Jun 11, 2014

@author: Umapathi
'''

import json

class Object:
    '''
    classdocs
    '''


    #def __init__(self, params):
     #   '''
     #   Constructor
     #   '''
    def toJson(self):
            json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)