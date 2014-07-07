'''
Created on Jun 11, 2014

@author: Umapathi
'''

import json
import decimal
from editor.models import Station,Marker,Media
from editor.models import Polyline

class Object:
    '''
    classdocs
    '''


    #def __init__(self, params):
     #   '''
     #   Constructor
     #   '''
    def toJson(self):
        if isinstance(self,decimal.Decimal):
            self = float(self)
            print(self)
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

#class to write the title of trial
class TitleEvents:
    
    def __init__(self,trailName):
        self.name = "Title"
        self.attributes = {"ledTitle":trailName}
        self.type = "title"
        
    def writeEvent(self,name,attributeName,attrib):
        self.name = name
        self.attributes = {attributeName:attrib}
        self.type = name
        
    def asJson(self):
        
        return dict(
                    name = self.name,
                    attributes = self.attributes,
                    type = self.type)
               
        

#class to write stations and swingpoints to json file    
class Station_SwingPointEvents:
    
    index = 0
    
    def __init__(self,route):
        
        self.stations = Station.objects.filter(route=route)
        self.stationIndex = 0
        self.swingPointIndex = 0
        self.swingStationIndex = 0
        self.swingIndex = 0
        
    def PolylineIndex(self,polyline):
        
        stationFound = False
        for s in self.stations:
            if(s.index == polyline.index):
                print(s.index)
                print(polyline.index)
                self.name = "station"+str(self.stationIndex+1)
                self.type = "region"
                self.attributes = polyline.as_json()
                action = {u"enter-region":[u"disableStation1Compass",u"stationEnterAudio"]}
                self.actions = action
                self.stationIndex+=1
                stationFound = True
                break
        
        if(stationFound!=True):
            self.swingIndex = polyline.index
            self.getSwingPointIndex()
            self.name = "station"+str(self.swingStationIndex)+"_swingpoint"+str(self.swingPointIndex+1)
            self.type = "region"
            self.attributes = polyline.as_json()
            action = {u"enter-region":[u"disableStation1Compass",u"stationEnterAudio"]}
            self.actions = action
            self.swingPointIndex+=1
            
    
    def as_json(self):
        
        return dict(
                    name = self.name,
                    type = self.type,
                    attributes = self.attributes,
                    action = self.actions)
        
    def getSwingPointIndex(self):
        
        i=0
        print(self.swingIndex)
        while(i<len(self.stations)-1):
            station1 = self.stations[i].index
            station2 = self.stations[i+1].index
            if((station1 < self.swingIndex) and (self.swingIndex < station2)):
                self.swingStationIndex=station1+1
                break
            i+=1
            
class MarkerEvent:
    
    def __init__(self,route):
        
        self.markers = Marker.objects.filter(route=route)
        self.route = route
    
    
    def markersIndex(self,marker_object,media_object):
        
        
        for marker in self.markers:
            if(marker.index == marker_object.index):
                self.name = marker.name
                self.type = "marker"
                self.attributes = marker.as_json()
                action = {u"marker-found":[u"MarkerUnDetect",media_object.eventName]}
                self.actions = action
                
    
    def as_json(self):
        return dict(
                    name = self.name,
                    type = self.type,
                    attributes = self.attributes,
                    action = self.actions)

class MediaEvent:
    
    def __init__(self,media):
        
        self.media = media
    
    def mediaIndex(self,media_object):
        
        
        self.name = media_object.eventName
        self.type = media_object.type
        self.attributes = self.media_attributes()
        if(self.media.type == "image"):
            if(self.media.nextEventName!=None):
                action = {u"image-disappeared":[media_object.nextEventName]}
            else:
                action = {u"image-disappeared":[u"MarkerDetect",u"Done"]}
        self.actions = action
                
    def media_attributes(self):
        
        return dict(
                    imageName = self.media.filename,
                    imageSize = self.media.size,
                    collectItem = False)
    
    def as_json(self):
        return dict(
                    name = self.name,
                    type = self.type,
                    attributes = self.attributes,
                    action = self.actions)
