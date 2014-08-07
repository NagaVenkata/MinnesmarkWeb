'''
Created on Jun 11, 2014

@author: Umapathi
'''
# -*- coding: utf-8 -*-
import os
import json
import decimal
from PIL import Image
from django.utils.encoding import smart_str
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
        self.attributes = {"ledTitle":smart_str(trailName)}
        self.type = "title"
        
        
    def writeEvent(self,name,attributeName,attrib):
        self.name = name
        self.attributes = {attributeName:attrib}
        self.type = name
    
    def writeEventActions(self,name,type,action_type,action):
        self.name = name
        if(action!=None):
            self.actions = {action_type:action}
        else:
            self.actions = {action_type:[]}
        
        self.type = type
        
    def asJson(self):
        
        return dict(
                    name = self.name,
                    attributes = self.attributes,
                    type = self.type)
               
    def asJsonAction(self):
        
        return dict(
                    name = self.name,
                    actions = self.actions,
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
                    actions = self.actions)
        
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
                    actions = self.actions)

class MediaEvent:
    
    def __init__(self,media):
        
        self.media = media
    
    def mediaIndex(self,media_object):
        
        
        self.name = media_object.eventName
        self.type = media_object.type
        self.collectItem = media_object.treasure
        if(self.media.type == "image"):
            img = Image.open(media_object.filepath)
            self.width = img.size[0]
            self.height = img.size[1] 
            self.attributes = self.image_attributes()
        if(self.media.type == "audio"):
            self.attributes = self.audio_attributes()
        if(self.media.type == "video"):
            self.attributes = self.video_attributes()
        
        
        action = None
        if(self.media.type == "image"):
            if(self.media.nextEventName!=None):
                action = {u"image-disappeared":[media_object.nextEventName]}
            else:
                action = {u"image-disappeared":[u"MarkerDetect",u"Done"]}
        if(self.media.type == "audio"):
            if(self.media.nextEventName!=None):
                action = {u"audio-finished-playing":[media_object.nextEventName]}
            else:
                action = {u"audio-finished-playing":[u"MarkerDetect",u"Done"]}
        if(self.media.type == "video"):
            if(self.media.nextEventName!=None):
                action = {u"video-finished-playing":[media_object.nextEventName]}
            else:
                action = {u"video-disappeared":[u"MarkerDetect",u"Done"]}
                
        self.actions = action
                
    def image_attributes(self):
        
        return dict(
                    imageName = self.media.filename,
                    imageSize = self.media.size,
                    width = self.width,
                    heigth = self.height,
                    collectItem = self.collectItem)
        
    def audio_attributes(self):
        
        return dict(
                    filename = self.media.filename,
                    fileSize = self.media.size,
                    collectItem = self.collectItem)

    def video_attributes(self):
        
        return dict (
                    filename = self.media.filename,
                    fileSize = self.media.size,
                    filetype = os.path.splitext(self.media.filename)[1:],
                    collectItem = self.collectItem)
    
    def as_json(self):
        return dict(
                    name = self.name,
                    type = self.type,
                    attributes = self.attributes,
                    actions = self.actions)

class ModelEvent:
    def __init__(self,marker_object,media_object):
        self.name = marker_object.name
        self.type = "marker"
        self.modelName = os.path.splitext(media_object.filename)[0]
        self.modelName = self.modelName+".obj"
        self.attributes = dict(
                               markerSize = marker_object.markerSize,
                               modelName = self.modelName,
                               markerName = marker_object.markerName)
    def as_json(self):
        return dict(
                    name = self.name,
                    type = self.type,
                    attributes = self.attributes)
        

class Marker_Media:
    def __init__(self,name):
        self.markerName = name
        self.markersMedia=[]

    def setMarkerMedia(self,markerMedia):
        self.markersMedia.append(markerMedia)
    
    def getMarkerName(self):
        return self.markerName
    
    def getMarkerMedia(self):
        return self.markersMedia
    
class MinnesmarkObjWriter:
    def __init__(self,filename,filePath):
        
        self.filename = filename
        self.objfilename = filename
        self.objfilename = os.path.splitext(self.objfilename)[0]
         
        self.objWriter = open(filePath+self.objfilename+".obj","w+")
    
        self.objWriter.write("# generated by MinnesmarkEditor " + "0.1\n")
        self.objWriter.write("mtllib "+ self.objfilename+".mtl\n")
        self.objWriter.write("o " + self.objfilename+"\n")
        self.setVertices()
        self.setNormals()
        self.setVertexTextures()
        self.objWriter.write("usemtl Material\n")
        self.objWriter.write("s off\n")
        self.setFaces()
        
        self.objWriter.close()
        
        self.mtlWriter = open(filePath+self.objfilename+".mtl","w+")
        self.writeMtl()
        self.mtlWriter.close()
        
    def setVertices(self):
        
        self.objWriter.write("v "+"0.984484 1.015231 -0.030518 \n")
        self.objWriter.write("v "+"1.015181 -0.984533 -0.030566 \n")
        self.objWriter.write("v "+"1.015273 -0.984533 0.027363 \n")
        self.objWriter.write("v "+"0.984575 1.015231 0.027412 \n")
            
            
        self.objWriter.write("v "+"-1.015273 0.984533 -0.027363 \n")
        self.objWriter.write("v "+"-1.015181 0.984533 0.030566 \n")
        self.objWriter.write("v "+"-0.984484 -1.015231 0.030518 \n")
        self.objWriter.write("v "+"-0.984575 -1.015232 -0.027412 \n")
        
    def setNormals(self):
        
        self.objWriter.write("vn "+"0.0f -1.0 0.0 \n")
        self.objWriter.write("vn "+"0.0 1.0 0.0 \n")
        self.objWriter.write("vn "+"1.0 0.0 0.0 \n")
        self.objWriter.write("vn "+"-0.0 -0.0 1.0 \n")
        self.objWriter.write("vn "+"-1.0 -0.0 -0.0 \n")
        self.objWriter.write("vn "+"0.0 0.0 -1.0 \n")
        
    def setVertexTextures(self):
        
        self.objWriter.write("vt "+"0.0 0.0 \n")
        self.objWriter.write("vt "+"1.0 0.0 \n")
        self.objWriter.write("vt "+"1.0 1.0 \n")
        self.objWriter.write("vt "+"0.0 1.0 \n")
        
    def setFaces(self):
        
        self.objWriter.write("f "+"1/1/1 2/2/1f 3/3/1 4/4/1 \n")
        self.objWriter.write("f "+"5/1/2 6/2/2 7/3/2 8/4/2 \n")
        self.objWriter.write("f "+"1/1/3 5/2/3 8/3/3 2/4/3 \n")
        self.objWriter.write("f "+"2/1/4 8/2/4 7/3/4 3/4/4 \n")
        self.objWriter.write("f "+"3/1/5 7/2/5 6/3/5 4/4/5 \n")
        self.objWriter.write("f "+"5/1/6 1/2/6 4/3/6 6/4/6 \n")
        
    def writeMtl(self):
        
        self.mtlWriter.write("# generated by MinnesmarkEditor " + "0.1\n")
        self.mtlWriter.write("# Material Count 1\n")
                  
                  
        self.mtlWriter.write("newmtl Material\n");
        self.mtlWriter.write("Ns 96.078431 \n")
        self.mtlWriter.write("Ka 0.000000 0.000000 0.000000 \n")
        self.mtlWriter.write("Kd 0.640000 0.640000 0.640000 \n")
        self.mtlWriter.write("Ks 0.500000 0.500000 0.500000 \n")
        self.mtlWriter.write("Ni 1.000000 \n")
        self.mtlWriter.write("d 1.000000 \n")
        self.mtlWriter.write("illum 2 \n")
        self.mtlWriter.write("map_Kd "+self.filename+" \n")
        self.mtlWriter.write("\n")
