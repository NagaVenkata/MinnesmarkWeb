# -*- coding: utf-8 -*-
import json
import os
import decimal
from django.utils.encoding import smart_str
import codecs
from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.exceptions import ValidationError,NON_FIELD_ERRORS
from editor import models
from PIL import Image
import shutil 
import editor
import imghdr
import sndhdr
from reportlab.pdfgen import canvas
from editor.models import Media, Route, Station, Polyline, Marker
from minnesmark.settings import PROJECT_ROOT
from editor.jsonObject import TitleEvents
from editor.jsonObject import Station_SwingPointEvents,MarkerEvent,MediaEvent,ModelEvent,Marker_Media,MinnesmarkObjWriter,StartMediaEvent,StationMediaEvent,CompassEvents

# Login_required means that the user has to be looged in to see that specific page

#Get all route that the owner has created
def get_all_routes_from_user(user_id):
    routes = Route.objects.filter(user_id=user_id)
    return routes

# /editor
# Displays when no route is selected
@login_required
def render_page_no_route(request):
    routes = get_all_routes_from_user(request.user.id)
    return render_to_response('editor/norouteselected.html', {'routes': routes},
                              context_instance=RequestContext(request))

# /edtior/station/<route_id>
# Render page with editor
@login_required
def render_page(request,route_id):
    routes = get_all_routes_from_user(request.user.id)
    route = validateRoute(route_id,request.user)
    if route is False:
        return HttpResponseRedirect('/editor')

    return render_to_response('editor/editor.html', {'routes': routes,'cur_route':route_id},
                              context_instance=RequestContext(request))

# /editor/general/<route_id>
# Renders general page with startmedia and route name
@login_required
def render_page_general(request,route_id):
    routes = get_all_routes_from_user(request.user.id)
    route = validateRoute(route_id,request.user)
    if route is False:
        return HttpResponseRedirect('/editor')

    if request.is_ajax():
            print("ajax request")
            if(request.method=="POST"):
                response_data = {}
                try:
                    json_str = request.body.decode(encoding='UTF-8')
                    json_obj = json.loads(json_str)
                    start_media = json_obj['start_media']
                    print(len(start_media))
                    order_count=1
                    if(len(start_media)>0):
                        for startMedia in start_media:
                            media_object = Media.objects.filter(id=startMedia['id'])
                            media = media_object[0]
                            media.order = order_count
                            media.options = startMedia['option']
                            media.save()
                            order_count +=1
                        resetStartMediaEventNames(route_id,request.user)
                except ValidationError as e:
                    print(e.args)
                    response_data['result'] = 'failed'
                    response_data['message'] = 'Kunde inte ladda data'
            
                return HttpResponse(json.dumps(response_data), content_type="application/json")

    route_name = route.name
    #If POST request to page
    if request.method == 'POST':
        success = False
        media_id = -1
        
        if request.user.is_authenticated():

            try:
                #Runs if you want to delete a media in startmedia
                success = delete_media(request.POST['delmedia'], request.user.id,route_id,0,0)
            except:
                #otherwise you want to upload a media
                userName = request.user.username
                userId = request.user.id
                #print(request.user.username)
                #print(request.user.id)
                #print(request.FILES['media_file'])
                #print(route_id)
                success, media_id = handle_upload(request,request.FILES['media_file'],route_id,0,0
                                                  )
                print(media_id)
        #TODO some kind of validation
        if (success):
            pass
            
            #media_msg =
        else:
            print("Fuck...")

    #TODO save order of objects in list
    #Get all media set to startmedia
    start_media = []
    for m in Media.objects.filter(route=route,mediatype=Media.STARTMEDIA, user=request.user).order_by('order'):
        start_media.append(m.as_json())
    
    return render_to_response('editor/general.html', {'start_media':start_media,'routes': routes,'cur_route':route_id,'cur_route_name':route_name},
                              context_instance=RequestContext(request))

# /editor/media/<route_id>
# render All stations to be able to add media
@login_required
def render_page_media(request,route_id):
    routes = get_all_routes_from_user(request.user.id)

    route = validateRoute(route_id,request.user)
    
    if route is False:
        return HttpResponseRedirect('/editor')

    if route.user == request.user or request.user.is_superuser:
        stations = Station.objects.filter(route=route)
        
        return render_to_response('editor/media.html',
                                  {'routes': routes,
                                   'cur_route':route_id,
                                   'stations':stations},
                              context_instance=RequestContext(request))
    else:
        redirect('/account/login')
        
# /editor/media/marker
# render All stations to be able to add media
@login_required
def render_page_marker(request,route_id,marker_id):
    routes = get_all_routes_from_user(request.user.id)
    markerName = "Markör"+str(marker_id) 
    
    
    route = validateRoute(route_id,request.user)
    if route is False:
        return HttpResponseRedirect('/editor')
   
    if route.user == request.user or request.user.is_superuser:
        
        if request.is_ajax():
            print("ajax request")
            if(request.method=="POST"):
                response_data = {}
                try:
                    json_str = request.body.decode(encoding='UTF-8')
                    json_obj = json.loads(json_str)
                    markers_media = json_obj['markers_media']
                    print(len(markers_media))
                    order_count=1
                    if(len(markers_media)>0):
                        for marker_media in markers_media:
                            media_object = Media.objects.filter(id=marker_media['id'])
                            media = media_object[0]
                            media.order = order_count
                            media.options = marker_media['option']
                            media.save()
                            order_count +=1
                        resetMarkerEvents_nextEvents(route_id,request.user,marker_id)
                except ValidationError as e:
                    print(e.args)
                    response_data['result'] = 'failed'
                    response_data['message'] = 'Kunde inte ladda data'
            
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            
            print(request.GET['id'])
            print(request.GET['type'])
            marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
            media_object = Media.objects.filter(id=request.GET['id'],route=route,marker=marker_object[0])
            media = media_object[0]
            print(media.options)
            print(media.id)
            try:
                #print(Media.PANORAMA)           
                media.options = request.GET['type']
                media.save()
                media_object = Media.objects.filter(id=request.GET['id'],route=route,marker=marker_object[0])
                print("media options "+str(media_object[0].options))
                if(media_object[0].options == 2):
                    writeObjFile(media_object[0].filepath,request,route_id,media_object[0].filename)
            except ValidationError as e:
                print(e.args)
            
            marker_media = []
            for m in Media.objects.filter(route=route,marker=marker_object[0], user=request.user).order_by('order'):
                marker_media.append(m.as_json())
            
            #media_option = None
        
            #if(len(marker_media) == 1):
            #    media_option = marker_media[0]['options']
        
            #if(len(marker_media)>1):
            #   print(marker_media[len(marker_media)-1]['options'])
            #   media_option = marker_media[len(marker_media)-1]['options']

            media_type = request.GET['type']    
            return HttpResponse(media_type)
            
        
        #stations = Station.objects.filter(route=route)
        marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
        if(len(marker_object)==0):
            save_marker_to_database(request,route_id,marker_id)
        marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
        
        if(request.method == 'POST'):
            try:
                print(request.POST['delmedia'])
                #Runs if you want to delete a media in startmedia
                success = delete_media(request.POST['delmedia'], request.user.id,route_id,0,marker_id)
            except:
                #otherwise you want to upload a media
                success, media_id = handle_upload(request,request.FILES['media_file'],route_id,0,marker_id
                                                  )
                print(marker_id)
        
        marker_media = []
        for m in Media.objects.filter(route=route,marker=marker_object[0], user=request.user).order_by('order'):
            marker_media.append(m.as_json())
            
        print(marker_media)
        
        media_option = None
        
        if(len(marker_media) == 1):
            media_option = marker_media[0]['options']
        
        if(len(marker_media)>1):
            print(marker_media[len(marker_media)-1]['options'])
            media_option = marker_media[len(marker_media)-1]['options']
        
        #print(marker_media)
        return render_to_response('editor/markerMediaPage.html',
                                  {'marker_media':marker_media,
                                   'routes': routes,
                                   'cur_route':route,
                                   'marker_id':marker_id,
                                   'marker_name':markerName,
                                   'prev_media_type':media_option
                                   },
                              context_instance=RequestContext(request))
    else:
        redirect('/account/login')

def writeObjFile(fileName,request,route_id,name):
    print(fileName)
    
    path = PROJECT_ROOT
    os.chdir(path)
    
    os.chdir('..')
    
    try:
        #if User hasen't uploaded anything yet, create folder
        os.mkdir(request.user.username+"/")
    except:
        pass
    
    route = Route.objects.filter(id=route_id)
    
    os.chdir(request.user.username)
    
    try:
        #get the route name and make a directory with that name
        if(route[0].name!="Ny Route"):
            os.mkdir(route[0].name)
            os.chdir(route[0].name)
        else:
            os.mkdir(route[0].id)
            os.chdir(route[0].id)
    except:
        pass
    
    if(route[0].name!="Ny Route"):
        os.chdir(route[0].name)
    else:
        os.chdir(route[0].id)
        
    print(os.getcwd())
    
    try:
        os.mkdir('osg_obj')
        os.chdir('osg_obj')
    except:
        pass
    
    
    print(os.getcwd())
    #folder = os.getcwd()


    #change to user folder
    #os.chdir(folder + '/osg_obj/')
    
    desPath = os.getcwd() 
    
    print("despath1 "+desPath)
    
    shutil.copy(fileName,desPath+"/osg_obj/")
    
    
    
    img = Image.open(desPath+'/osg_obj/'+name)
    
    width=0
    height=0
    
    if(img.size[0]<256):
        width=256
    
    if(img.size[1]<256):
        height=256
    
    if(img.size[0]<350):
        width=256
    
    if(img.size[1]<350):
        height=256
        
    if(img.size[0]>350 and img.size[0]<512):
        width=512
    
    if(img.size[1]>350 and img.size[1]<512):
        height=512
        
    if(img.size[0]>512):
        width=512
    
    if(img.size[1]>512):
        height=512
    
    print("despath "+desPath)
    
    texturefile = os.path.splitext(name)[0]+".jpg"
    
    print("texture name "+texturefile)
       
    if((width != 0) and (height != 0)):
        print(str(width)+" "+str(height))   
        img1 = img.resize((width,height),Image.ANTIALIAS)
        img1.save(desPath+'/osg_obj/'+texturefile)
        
    
    MinnesmarkObjWriter(texturefile,desPath+'/osg_obj/')   
   
    
        
def save_marker_to_database(request,route_id,marker_id):
    print(route_id)
    print(marker_id)
    
    path = PROJECT_ROOT
    os.chdir(path)
    # Move up one
    os.chdir('..')
    
    folder = os.getcwd()
    
    path = folder+"/static/globalmarkers/patt.marker"+str(marker_id)
    
    print(os.path.getsize(path))
    
    filesize = os.path.getsize(path)
    
    route = Route.objects.get(id=route_id)
    #if route.user == request.user:
    #    route.name = json_obj['name'];
    #    route.save()
    #    response_data['result'] = 'ok'
    #    response_data['message'] = 'Sparat'
    #    return HttpResponse(json.dumps(response_data), content_type="application/json")
    #else:
    #    response_data['result'] = 'failed'
    #    response_data['message'] = 'Du äger inte denna rutt.'
    #    return HttpResponse(json.dumps(response_data), content_type="application/json")

    #Save marker
    try:
            #Marker.objects.filter(route = route).delete()
            marker = Marker(route=route,
                            index = marker_id,
                            name = "marker"+str(marker_id),
                            markerName = "patt.marker"+str(marker_id),
                            type = "marker",
                            markerSize = filesize,
                            angle = 0,
                            collectItem = False
                           )
            marker.save()
    except ValidationError as e:
        print(e.args)
            

# /editor/publish/<route_id>
# Renders publish page of route
@login_required
def render_page_publish(request,route_id):
    routes = get_all_routes_from_user(request.user.id)
    route = validateRoute(route_id,request.user)
    if route is False:
        return HttpResponseRedirect('/editor')
    if request.is_ajax():
        print("ajax request")
        response_data= {}
        if(request.method=="GET"):
            #response = HttpResponse(content_type='application/pdf')
            #response['Content-Disposition'] = 'inline; filename="markers.pdf"'
            #c = canvas.Canvas("/Users/Umapathi/Desktop/text.pdf")
            markers = []
    
            #for each marker get the media associated with it
            for m in Marker.objects.filter(route=route):
                marker = Marker_Media(m.name) 
                for media in Media.objects.filter(route=route,marker=m,user=request.user).order_by('order'):
                    marker.setMarkerMedia(media.as_json())
                if(len(marker.getMarkerMedia())!=0):
                    markers.append(marker)
            path = PROJECT_ROOT
            os.chdir(path)
            # Move up one
            os.chdir('..')
    
            folder = os.getcwd()
            path = folder+"/static/temp/"+str(request.user)+"/markers.pdf"
            c = canvas.Canvas(path)
            i=1
            
            path = PROJECT_ROOT
            os.chdir(path)
            # Move up one
            os.chdir('..')
    
            folder = os.getcwd()

            
            for marker in markers:
                    
                path = folder+"/static/globalmarkers/pattern"+str(i)+".png"
                c.drawImage(path,200,400)
                print("markers "+str(len(marker.getMarkerMedia())))
                num_media = len(marker.getMarkerMedia())-1
                print("media "+str(num_media))
                media = "Media:"
                for j in range(0,len(marker.getMarkerMedia())):
                    print("marker media")
                    if(j==len(marker.getMarkerMedia())-1):
                        media = media+marker.getMarkerMedia()[len(marker.getMarkerMedia())-1]['name']
                    print(marker.getMarkerMedia()[j])
                    media = media+marker.getMarkerMedia()[j]['name']+","
                #media = media+marker.getMarkerMedia()[len(marker.getMarkerMedia())-1]['name']
                c.drawString(100,200,media)
                #print(c._pagesize)
                c.showPage()
                i=i+1
            #c.drawImage("/Users/Umapathi/Desktop/MinnesmarkWeb/static/globalmarkers/pattern2.png",200,400)
            #c.drawString(100,200,"Minnesmark Editor Page2")
            #c.showPage()
            c.save()
            print(request.user)
            response_data['pdf_url'] = '/static/temp/'+str(request.user)+'/markers.pdf'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if(request.method=="POST"):
            response_data = {}
            try:
                json_str = request.body.decode(encoding='UTF-8')
                json_obj = json.loads(json_str)
                stations_media = json_obj['stations_media']
                if(len(stations_media)>0):
                    for station_media in stations_media:
                        media_object = Media.objects.filter(id=station_media['id'])
                        media = media_object[0]
                        media.treasure = station_media['checked']
                        media.save()

                
                markers_media = json_obj['markers_media']
                print(len(markers_media))
                print("lenght "+str(len(json_obj)))
                if(len(markers_media)>0):
                    for marker_media in markers_media:
                        media_object = Media.objects.filter(id=marker_media['id'])
                        media = media_object[0]
                        media.treasure = marker_media['checked']
                        media.save()
            
            except:
                response_data['result'] = 'failed'
                response_data['message'] = 'Kunde inte ladda data'
            
            publish_trail(request,route_id)
            route.published = True
            route.save()
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    #Get all media set to startmedia
    start_media = []
    for m in Media.objects.filter(route=route,mediatype=Media.STARTMEDIA, user=request.user).order_by('order'):
        start_media.append(m.as_json())

    stations = []
    
    #for each marker get the media associated with it
    for station in Station.objects.filter(route=route):
        stationName = "Station"+str(station.number)
        station1 = Marker_Media(stationName) 
        for media in Media.objects.filter(route=route,station_id=station.number,user=request.user).order_by('order'):
            station1.setMarkerMedia(media.as_json)
        if(len(station1.getMarkerMedia())!=0):
            stations.append(station1)

    
    markers = []
    
    #for each marker get the media associated with it
    for m in Marker.objects.filter(route=route):
        marker = Marker_Media(m.name) 
        for media in Media.objects.filter(route=route,marker=m,user=request.user).order_by('order'):
            marker.setMarkerMedia(media.as_json)
        if(len(marker.getMarkerMedia())!=0):
            markers.append(marker)
    
    
         
    return render_to_response('editor/publish.html', {'routes': routes,'cur_route':route_id,'start_media':start_media,"stations":stations,"markers":markers},
                              context_instance=RequestContext(request))


def publish_trail(request,route_id):
    routes = get_all_routes_from_user(request.user.id)
    route = validateRoute(route_id,request.user)
    stations = Station.objects.filter(route=route)
    points = Polyline.objects.filter(route=route)
    markers = Marker.objects.filter(route=route)
    
    
    attrib = [ ]
    
    title = TitleEvents(route.name)
    
    attrib.append(title.asJson())
    
    num_stations = 0
    
    for s in Station.objects.filter(route=route):
        # marker = Marker_Media(m.name) 
        media =  Media.objects.filter(route=route,station=s,user=request.user).order_by('order')
        if(len(media)>0):
            num_stations = num_stations+1 
        

    if(num_stations>0):
        title.writeEvent("NumberOfRegions","numRegions", len(stations))
        attrib.append(title.asJson())
        title.writeEvent("compassView","showCompassView",True)
        attrib.append(title.asJson())
    
    actions = ["Start"]
    title.writeEventActions("launch","generic","application-launched",actions)
    attrib.append(title.asJsonAction())
    
    markers1 = [ ]
    
    num_markers = [ ]
    
    for m in Marker.objects.filter(route=route):
        marker = Marker_Media(m.name) 
        for media in Media.objects.filter(route=route,marker=m,user=request.user).order_by('order'):
            marker.setMarkerMedia(media.as_json())
        num_markers.append(marker)
    
    if(len(stations)>0):
        markers1.append("compassView")
    
    i=1    
    for p in points:
        if(p.swingPoint==False and i==1):
            markers1.append("enableStation1Compass")
        if(p.swingPoint==False and i!=1):
            markers1.append("disableStation"+str(i)+"Compass")
        if(p.swingPoint==True):
            markers1.append("disableStation"+str(p.stationIndex)+"SwingPoint"+str(p.index)+"Compass")
        i=i+1    
              
        
    for markers_media in num_markers:
        if(len(markers_media.getMarkerMedia())>0):
            markers1.append(markers_media.getMarkerName()) 
            
    start_media = Media.objects.filter(route=route,user=request.user,mediatype=Media.STARTMEDIA).order_by('order')
    
    if(len(start_media)!=0):
        markers1.append(start_media[0].eventName)
    
    title.writeEventActions("Start","start","application-start",markers1)
    attrib.append(title.asJsonAction())
    
    collectItems = 0 
    #collect items for markers
    for m in Marker.objects.filter(route=route):
        marker = Marker_Media(m.name) 
        for media in Media.objects.filter(route=route,marker=m,user=request.user):
            if(media.treasure==True):
                collectItems = collectItems+1
                
    title.writeEvent("NumberOfCollectItems","numCollectItems",collectItems)
    attrib.append(title.asJson()) 
    
    if(len(start_media)!=0):
        for media in start_media:
            start_media_event = StartMediaEvent(media)
            start_media_event.mediaIndex(media)
            attrib.append(start_media_event.as_json())
            
           
    
    #attrib.append(attr)
    #attrib.append(attr1)
    if(num_stations>0):
        station = Station_SwingPointEvents(route)
        for p in points:
            station.PolylineIndex(p,request.user)
            attrib.append(station.as_json())
    
    if(num_stations>0):
        index=0
        i=0
        stations = Station.objects.filter(route=route)
        while(i<len(stations)-1):
            index = index+1
            station_media = Media.objects.filter(route=route,station=stations[i],user=request.user)
            next_station_media = Media.objects.filter(route=route,station=stations[i+1],user=request.user)
            for station_eventMedia in station_media:
                stationEventMedia = StationMediaEvent(route)
                if(len(next_station_media)!=0 or i<len(stations)-1):
                    stationEventMedia.mediaIndex(station_eventMedia, stations[i],stations[i+1],index)
                else:
                    stationEventMedia.mediaIndex(station_eventMedia, stations[i],None,index)
                attrib.append(stationEventMedia.as_json())
            i=i+1
    
    i=0
    for p in points:
        if(p.swingPoint==False):
            compassEvent = CompassEvents("enableStation"+str(i+1)+"Compass")
            compassEvent.writeEvents(True, "station"+str(i+1))
            attrib.append(compassEvent.as_json())
            
            compassEvent = CompassEvents("disableStation"+str(i+1)+"Compass")
            compassEvent.writeEvents(False, "station"+str(i+1))
            attrib.append(compassEvent.as_json())
            i=i+1
        if(p.swingPoint==True):
            compassEvent = CompassEvents("enableStation"+str(p.stationIndex)+"SwingPoint"+str(p.index)+"Compass")
            compassEvent.writeEvents(True, "station"+str(p.stationIndex)+"_swingPoint"+str(p.index))
            attrib.append(compassEvent.as_json())
            
            compassEvent = CompassEvents("disableStation"+str(p.stationIndex)+"SwingPoint"+str(p.index)+"Compass")
            compassEvent.writeEvents(False, "station"+str(p.stationIndex)+"_swingPoint"+str(p.index))
            attrib.append(compassEvent.as_json())
                        

    
#     markerEvent = MarkerEvent(route)
#     
#     for marker in markers:
#         marker_media = Media.objects.filter(route=route,marker=marker)
#         if(len(marker_media)!=0):
#             markerEvent.markersIndex(marker,marker_media[0])
#             attrib.append(markerEvent.as_json())
            
    writeMarkerEvent = True
    
    marker_count = 1
            
    for marker in markers:
        marker_media = Media.objects.filter(route=route,marker=marker)
        if(len(marker_media)!=0):
            for media in marker_media:
                if(media.options!=2):
                    if(writeMarkerEvent):
                        markerEvent = MarkerEvent(route)
                        markerEvent.markersIndex(marker,marker_media[0])
                        attrib.append(markerEvent.as_json())
                        writeMarkerEvent = False
                        writeMarkerFiles(marker.name,marker_count,request.user,route_id)
                        marker_count = marker_count+1
                        
                    mediaEvent = MediaEvent(media,num_stations)
                    mediaEvent.mediaIndex(media)
                    attrib.append(mediaEvent.as_json())
                else:
                    writeMarkerFiles(marker.name,marker_count,request.user,route_id)
                    marker_count = marker_count+1
                    modelEvent = ModelEvent(marker,media)
                    attrib.append(modelEvent.as_json())
                    
        writeMarkerEvent = True
                
    title.writeEventActions("Done","done","application-done",None)
    attrib.append(title.asJsonAction())      
    
    print(json.dumps(attrib,ensure_ascii=False))
    
    path = PROJECT_ROOT
    os.chdir(path)
    # Move up one
    os.chdir('..')
    #Enter user folder
    #os.chdir('users/')
    #folder = os.getcwd()

    try:
        #if User hasen't uploaded anything yet, create folder
        os.mkdir(request.user.id + '/')
    except:
        pass

   
    #change to user folder
    os.chdir(request.user.username)
    
    
    if(route.name!="Ny Route"):
        os.chdir(route.name)
    else:
        os.chdir(route.id)
        
    print(os.getcwd())
    
    folder = os.getcwd()

    #Fullpath to file
    fullpath = folder + "/" +route.name+".json"
    
    

    #Try to create file
    try:
        with open(fullpath, 'w+',encoding='utf-8') as f:
            json.dump(attrib,f,sort_keys = True, indent = 4,ensure_ascii=False)
    except ValidationError as e:
        print(e.args)
        return False
    
        
def writeMarkerFiles(markerName,marker_id,user,route_id):
    
    path = PROJECT_ROOT
    os.chdir(path)
    # Move up one
    os.chdir('..')
    
    folder = os.getcwd()
    
    patternPath = folder+"/static/globalmarkers/patt.marker"+str(marker_id)

    markerPath = folder + "/static/globalmarkers/pattern"+str(marker_id)+".png"
    
    #path = PROJECT_ROOT
    #os.chdir('..')
    
    print("markers write "+os.getcwd())
    
    try:
        #if User hasen't uploaded anything yet, create folder
        os.mkdir(user.username+"/")
    except:
        pass
    
    route = Route.objects.filter(id=route_id)
    
    os.chdir(user.username)
    
    try:
        #get the route name and make a directory with that name
        if(route[0].name!="Ny Route"):
            os.mkdir(route[0].name)
            os.chdir(route[0].name)
        else:
            os.mkdir(route[0].id)
            os.chdir(route[0].id)
    except:
        pass
    
    if(route[0].name!="Ny Route"):
        os.chdir(route[0].name)
    else:
        os.chdir(route[0].id)
        
    print(os.getcwd())
    
    
    try:
        os.mkdir('markers')
        os.chdir('markers')
    except:
        os.chdir('markers')
        pass
    
    
    print(os.getcwd())
    #folder = os.getcwd()


    #change to user folder
    #os.chdir(folder + '/osg_obj/')
    
    desPath = os.getcwd() 
    
    print(desPath)
    
    
    shutil.copy(patternPath,desPath)
    shutil.copy(markerPath,desPath)

    

    
# /editor/media/<route_id>/station/<station_id>
# NOT DONE IN URL !!!!!
# TODO render right media with files
@login_required
def render_page_addMedia(request,route_id,station_id):
    routes = get_all_routes_from_user(request.user.id)
    print(request)
    route = validateRoute(route_id,request.user)
    if route is False:
        return HttpResponseRedirect('/editor')
            
            
    
    print("entered")

    if route.user == request.user or request.user.is_superuser:
        
        if request.is_ajax():
            print("ajax request")
            if(request.method=="POST"):
                response_data = {}
                try:
                    json_str = request.body.decode(encoding='UTF-8')
                    json_obj = json.loads(json_str)
                    stations_media = json_obj['stations_media']
                    print(len(stations_media))
                    order_count=1
                    if(len(stations_media)>0):
                        for station_media in stations_media:
                            media_object = Media.objects.filter(id=station_media['id'])
                            media = media_object[0]
                            media.order = order_count
                            media.options = station_media['option']
                            media.save()
                            order_count +=1
                        resetStationEvents_nextEvents(route_id,request.user,station_id)
                except ValidationError as e:
                    print(e.args)
                    response_data['result'] = 'failed'
                    response_data['message'] = 'Kunde inte ladda data'
            
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            
            print(request.GET['id'])
            print(request.GET['type'])
            station_object = Station.objects.filter(route_id=route_id,id=station_id)
            media_object = Media.objects.filter(id=request.GET['id'],route=route,station=station_object[0])
            media = media_object[0]
            print(media.options)
            print(media.id)
            try:
                #print(Media.PANORAMA)           
                media.options = request.GET['type']
                media.save()
                media_object = Media.objects.filter(id=request.GET['id'],route=route,station=station_object[0])
                print("media options "+str(media_object[0].options))
            except ValidationError as e:
                print(e.args)
            
            marker_media = []
            for m in Media.objects.filter(route=route,station=station_object[0], user=request.user).order_by('order'):
                marker_media.append(m.as_json())
            
            #media_option = None
        
            #if(len(marker_media) == 1):
            #    media_option = marker_media[0]['options']
        
            #if(len(marker_media)>1):
            #   print(marker_media[len(marker_media)-1]['options'])
            #   media_option = marker_media[len(marker_media)-1]['options']

            media_type = request.GET['type']    
            return HttpResponse(media_type)
            
        
        #stations = Station.objects.filter(route=route)
        station_object = Station.objects.filter(route_id=route_id,id=station_id)
        if(request.method == 'POST'):
            try:
                print(request.POST['delmedia'])
                #Runs if you want to delete a media in startmedia
                success = delete_media(request.POST['delmedia'], request.user.id,route_id,station_id,0)
            except:
                #otherwise you want to upload a media
                success, media_id = handle_upload(request,request.FILES['media_file'],route_id,station_id,0
                                                  )
                print(station_id)
        
        station_media = []
        for m in Media.objects.filter(route=route,station_id=station_object[0].number, user=request.user).order_by('order'):
            station_media.append(m.as_json())
            
        print(station_media)
        
        media_option = None
        
        if(len(station_media) == 1):
            media_option = station_media[0]['options']
        
        if(len(station_media)>1):
            print(station_media[len(station_media)-1]['options'])
            media_option = station_media[len(station_media)-1]['options']
        
        #print(marker_media)
        return render_to_response('editor/addMedia.html',
                                  {'station_media':station_media,
                                   'routes': routes,
                                   'cur_route':route,
                                   'station_id':station_id,
                                   'station_name':"Station1",
                                   'prev_media_type':media_option
                                   },
                              context_instance=RequestContext(request))
    else:
        redirect('/account/login')


# Function for uploading media
#===============================================================================
# def handle_upload(f, username, user_id,route_id):
#     #Set Project Path
#     path = PROJECT_ROOT
#     os.chdir(path)
#     # Move up one
#     os.chdir('..')
#     #Enter user folder
#     os.chdir('users/')
#     folder = os.getcwd()
# 
#     try:
#         #if User hasen't uploaded anything yet, create folder
#         os.mkdir(username + '/')
#     except:
#         pass
# 
#     #change to user folder
#     os.chdir(username)
#     folder = os.getcwd()
# 
#     #Fullpath to file
#     fullpath = folder + "/" + f.name
#     
#     
# 
#     #Try to create file
#     try:
#         with open(fullpath, 'wb+') as destination:
#             for chunk in f.chunks():
#                 destination.write(chunk)
#     except:
#         return False
# 
#     print('Entered')
#     userobject = User.objects.get(id=user_id)
#     route_object = Route.objects.get(id=route_id)
#     media_count = Media.objects.filter(mediatype=Media.STARTMEDIA, user=userobject).count()
#     #Save media as STARTMEDIA
#     # TODO create any type of media and add to station
#     media = Media(route=route_object,
#                 filename=f.name,
#                 filepath=fullpath,
#                 size=f.size,
#                 treasure=False,
#                 mediatype=Media.STARTMEDIA,
#                 user=userobject,
#                 order=media_count + 1,
#                 station=None)
#     media.save()
#     #If media has beredirect('/editor')en saved return true
#     if media.pk > 0:
#         return True, media.pk
#     else:
#         return False
#===============================================================================

def handle_upload(request,f,route_id,station_id,marker_id):
    #Set Project Path
    path = PROJECT_ROOT
    os.chdir(path)
    # Move up one
    os.chdir('..')
    #Enter user folder
    #os.chdir('users/')
    #folder = os.getcwd()

    try:
        #if User hasen't uploaded anything yet, create folder
        os.mkdir(request.user.username + '/')
    except:
        pass

    #change to user folder
    os.chdir(request.user.username)
    
    route = Route.objects.filter(id=route_id)
    
    try:
        #get the route name and make a directory with that name
        if(route[0].name!="Ny Route"):
            os.mkdir(route[0].name)
            os.chdir(route[0].name)
        else:
            os.mkdir(route[0].id)
            os.chdir(route[0].id)
    except:
        pass
    
    if(route[0].name!="Ny Route"):
        os.chdir(route[0].name)
    else:
        os.chdir(route[0].id)
    
    folder = os.getcwd()
    
    if(isImageFile(f.name)):
        try:
            os.mkdir(folder+"/images")
            os.chdir(folder+"/images")
        except:
            os.chdir(folder+"/images")
    
    if(isAudioFile(f.name)):
        try:
            os.mkdir(folder+"/audios")
            os.chdir(folder+"/audios")
        except:
            os.chdir(folder+"/audios")
    if(isVideoFile(f.name)):
        try:
            os.mkdir(folder+"/videos")
            os.chdir(folder+"/videos")
        except:
            os.chdir(folder+"/videos")    
        
    
    folder = os.getcwd()
    
    
    #Fullpath to file
    fullpath = folder + "/" + f.name
    
    
    #Try to create file
    try:
        with open(fullpath, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        if(' ' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace(" ","_"))
            fullpath = fullpath.replace(" ","_")
            f.name = f.name.replace(" ","_")
        if('ö' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace("ö","o"))
            fullpath = fullpath.replace("ö","o")
            f.name = f.name.replace("ö","o")
        if('Ö' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace("Ö","O"))
            fullpath = fullpath.replace("Ö","O")
            f.name = f.name.replace("Ö","O")
        if('å' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace("å","a"))
            fullpath = fullpath.replace("å","a")
            f.name = f.name.replace("å","a")
        if('Å' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace("Å","A"))
            fullpath = fullpath.replace("Å","A")
            f.name = f.name.replace("Å","A")
        if('ä' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace("ä","a"))
            fullpath = fullpath.replace("ä","a")
            f.name = f.name.replace("ä","a")
        if('Ä' in str(fullpath)):
            os.rename(fullpath, str(fullpath).replace("Ä","A"))
            fullpath = fullpath.replace("Ä","A")
            f.name = f.name.replace("Ä","A")
        
            
    except:
        return False

    
    userobject = User.objects.get(id=request.user.id)
    route_object = Route.objects.get(id=route_id)
    
    if(station_id!=0):
        station_object = Station.objects.filter(route_id=route_id,id=station_id)
        station_media_count = Media.objects.filter(station_id=station_object[0].number,mediatype=Media.STATION_MEDIA,user=userobject).count()
    
    if(marker_id!=0):
        marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
    
    startmedia_count = 0
    media_count = 0
    
    if(station_id == 0 and marker_id == 0):
        startmedia_count = Media.objects.filter(mediatype=Media.STARTMEDIA, user=userobject).count()
        startMedia =  Media.objects.filter(mediatype=Media.STARTMEDIA,user = userobject)
    
    if(marker_id!=0):
        media_count = Media.objects.filter(marker=marker_object[0],mediatype=Media.AR_MEDIA, user=userobject).count()
        markers = Media.objects.filter(marker=marker_object[0],mediatype=Media.AR_MEDIA, user=userobject)
        
    print(route_object)    
    #print(marker_object[0])
    
    type=None
        
        
        
    media = None  
    eventName = None  
    
    if(station_id == 0 and marker_id == 0):
        #Save media as STARTMEDIA
        # TODO create any type of media and add to station
        
        eventName = None
        option = 0
        type = None
        
        #gets all the start media images 
        startmedia_images = Media.objects.filter(mediatype=Media.STARTMEDIA,user = userobject,options = 3)
        
        print("start media "+str(startmedia_count))
        
        if(isImageFile(f.name)):
            eventName = "start"+"_"+"Image"+str(startmedia_count+1)
            type="image"
            option=3
        if(isAudioFile(f.name)):
            eventName = "start"+"_"+"Audio"+str(startmedia_count+1)
            type="audio"
            option=0
        if(isVideoFile(f.name)):
            eventName = "start"+"_"+"Video"+str(startmedia_count+1)
            type="video"
            option = 0
        
        if(startmedia_count>=1):
            print("next event name "+eventName)
            startmedia = startMedia[startmedia_count-1]
            startmedia.nextEventName = eventName
            startmedia.save()
            nextEventName = None
        
        #eventName = f.name+str(media_count+1)
        media = Media(route=route_object,
                filename=f.name,
                filepath=fullpath,
                size=f.size,
                treasure=False,
                mediatype=Media.STARTMEDIA,
                user=userobject,
                order=startmedia_count + 1,
                options = option,
                station_id=None,
                marker=None,
                nextEventName=None,
                eventName=eventName,
                type=type)
    
    if(station_id != 0):
        #Save media as STARTMEDIA
        # TODO create any type of media and add to station
        
        eventName = None
        option = 0
        type = None
        
        #gets all the start media images 
        station_media = Media.objects.filter(mediatype=Media.STATION_MEDIA,user = userobject,station_id=station_object[0].number)
        
        print("station media "+str(station_media))
        
        station_index = station_object[0].number
        
        if(isImageFile(f.name)):
            eventName = "station"+str(station_index)+"_"+"Image"+str(station_media_count+1)
            type="image"
            option=3
        if(isAudioFile(f.name)):
            eventName = "station"+str(station_index)+"_"+"Audio"+str(station_media_count+1)
            type="audio"
            option=0
        if(isVideoFile(f.name)):
            eventName = "station"+str(station_index)+"_"+"Video"+str(station_media_count+1)
            type="video"
            option = 0
        
        if(len(station_media)>=1):
            print("next event name "+eventName)
            stationmedia = station_media[station_media_count-1]
            stationmedia.nextEventName = eventName
            stationmedia.save()
            nextEventName = None
        
        #eventName = f.name+str(media_count+1)
        media = Media(route=route_object,
                filename=f.name,
                filepath=fullpath,
                size=f.size,
                treasure=False,
                mediatype=Media.STATION_MEDIA,
                user=userobject,
                order=station_media_count + 1,
                options = option,
                station_id=station_object[0].number,
                marker=None,
                nextEventName=None,
                eventName=eventName,
                type=type)
    
        
    if(marker_id != 0):
        #Save media as STARTMEDIA
        # TODO create any type of media and add to station
    
        #eventName = "marker"+str(marker_id)+"_"+os.path.splitext(f.name)[1]
        
        marker_media = None
        nextEventName = None
        option = None
        
        
        if(isImageFile(f.name)):
            eventName = "marker"+str(marker_id)+"_"+"Image"+str(media_count+1)
            type="image"
            option=3
        if(isAudioFile(f.name)):
            eventName = "marker"+str(marker_id)+"_"+"Audio"+str(media_count+1)
            type="audio"
            option=None
        if(isVideoFile(f.name)):
            eventName = "marker"+str(marker_id)+"_"+"Video"+str(media_count+1)
            type="video"
            option = None    
        
            
        
        if(media_count>=1):
            #print(len(markers))
            #marker_media = Media.objects.filter(marker=marker_object[0],user=userobject)   
            markers[len(markers)-1].nextEventName = eventName
            markers[len(markers)-1].save()
            nextEventName = None
            
        
        media = Media(route=route_object,
                filename=f.name,
                filepath=fullpath,
                size=f.size,
                treasure=False,
                mediatype=Media.AR_MEDIA,
                user=userobject,
                order=media_count + 1,
                options = option,
                station_id=None,
                marker=marker_object[0],
                nextEventName=nextEventName,
                eventName = eventName,
                type=type)    
        
    media.save()
    #If media has beredirect('/editor')en saved return true
    if media.pk > 0:
        return True, media.pk
    else:
        return False

def isImageFile(fileName):
    #fileExt = imghdr.what(fileName)
    fileExt = os.path.splitext(fileName)[1] 
    
    if(fileExt == ".jpg" or fileExt == ".JPG" or fileExt == ".jpeg" or fileExt == ".JPEG" or fileExt == ".png" or fileExt == ".PNG"  or fileExt == ".bmp" or fileExt == ".BMP" or fileExt == ".gif" or fileExt == ".GIF"):
        return True
    else:
        return False
    
def isAudioFile(fileName):
    fileExt = os.path.splitext(fileName)[1]
    
    if(fileExt == ".aiff" or fileExt == ".AIFF" or fileExt == ".m4a"  or fileExt == ".M4A" or fileExt == ".mp3" or fileExt == ".MP3"):
        return True
    else:
        return False 

def isVideoFile(fileName):
    fileExt = os.path.splitext(fileName)[1]
    
    if(fileExt == ".m4v" or fileExt == ".M4V"):
        return True
    else:
        return False
        

#Get all route info for loading to editor
@login_required
def load_route_from_db(request,route_id):
    response_data = {}
    try:
        route = Route.objects.get(id = route_id,user=request.user)
    except Route.DoesNotExist:
        return HttpResponse(json.dumps("ERROR"), content_type="application/json")

    stations = Station.objects.filter(route=route)
    response_data["stations"] = []
    for s in stations:
        #print(s.as_json())
        response_data["stations"].append(s.as_json())
    points = Polyline.objects.filter(route=route)
    response_data["points"] = []
    for p in points:
        response_data["points"].append(p.as_json())
    
    print(json.dumps(response_data))
    return HttpResponse(json.dumps(response_data), content_type="application/json")


#Save route from editor
@login_required
def save_route_to_database(request):
    response_data = {}

    """Load JSON"""
    try:
        json_str = request.body.decode(encoding='UTF-8')
        json_obj = json.loads(json_str)
    except:
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte ladda data'
    #Delete all old entrys and save over them
    try:
        route_id = json_obj["route_id"]
        route = Route.objects.get(id=route_id)
        r_station = Station.objects.filter(route = route).delete()
        r_polyline = Polyline.objects.filter(route = route).delete()
    except:
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte ladda rutt från id'
    #Save all stations

    try:
        test = []
        for s in json_obj["stations"]:
            alreadyExist = False
            for x in test:
                if s["index"] == x:
                    alreadyExist = True
            test.append(s["index"])

            if alreadyExist:
                print("Station already exist")
            else:
                station = Station(route=route,
                              number=s["number"],
                              index=s["index"])
                station.save()
    except:
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte spara markörer'
    #Save positoins on polyline

    try:
        test = []
        for point in json_obj["points"]:
            alreadyExist = False
            for x in test:
                if point["index"] == x:
                    alreadyExist = True
            test.append(point["index"])

            if alreadyExist:
                print("Swingpoint already exist")
            else:
            #print(point)
                point = Polyline(route=route,
                                 latitude=point["latitude"],
                                 longitude=point["longitude"],
                                 index=point["index"],
                                 radius = point["radius"],
                                 shouldDisplayOnCompass = point["shouldDisplayOnCompass"],
                                 swingPoint = point["swingPoint"],
                                 stationIndex=point["stationIndex"])
                point.save()

        response_data['result'] = 'ok'
        response_data['message'] = 'Rutten sparades'
    except ValidationError as e:
        print(e.args) 
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte spara punkter'

    return HttpResponse(json.dumps(response_data), content_type="application/json")

#Create a new Route for signed in user
@login_required
def create_route(request):
    route = Route(user=request.user)
    route.save()
    return redirect('/editor/general/'+str(route.id))

#Save the name for the route (using AJAX)
@login_required
def save_route_name_to_db(request):
    response_data = {}

    """Load JSON"""
    try:
        json_str = request.body.decode(encoding='UTF-8')
        json_obj = json.loads(json_str)
    except:
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte ladda rutt från id'

    route = Route.objects.get(id=json_obj["route_id"])
    if route.user == request.user:
        route_name = json_obj['name']
        if(' ' in route_name):
            route_name = route_name.replace(" ","_")
        if('å' in route_name):
            route_name = route_name.replace("å","a")
        if('Å' in route_name):
            route_name = route_name.replace("Å","A")
        if('ä' in route_name):
            route_name = route_name.replace("ä","a")
        if('Ä' in route_name):
            route_name = route_name.replace("Ä","A")
        if('ö' in route_name):
            route_name = route_name.replace("ö","o")
        if('Ö' in route_name):
            route_name = route_name.replace("Ö","O")
            
        route.name = json_obj['name']
        route.save()
        response_data['result'] = 'ok'
        response_data['message'] = 'Sparat'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data['result'] = 'failed'
        response_data['message'] = 'Du äger inte denna rutt.'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

def delete_route(request,route_id):
    response_data = {}
    try:
        route = Route.objects.get(id=route_id)
        Route.objects.get(id=route_id).delete()
        Station.objects.filter(route=route).delete()
        Media.objects.filter(route=route).delete()
        response_data['message'] = 'hej'
    except ValidationError as e:
        response_data['message'] = 'hej'
        print(e.args())
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def delete_station(request):
    
    response_data = {}
    
    try:
        json_str = request.body.decode(encoding='UTF-8')
        json_obj = json.loads(json_str)
    except:
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte ladda data'
    #Delete all old entrys and save over them
    try:
        route_id = json_obj["route_id"]
        station_id = json_obj['station_id']
        route = Route.objects.get(id=route_id)
        
        stations = Station.objects.filter(route = route)
        
        next_station = None
        current_station = None
        next_stationIndex = -1
        
        print("stations "+str(len(stations)))
        
        for i in range(0, len(stations)-1):
            print("station index "+str(stations[i].index))
            if(stations[i].index==station_id):
                print("entered station id")
                if(i!=len(stations)):
                    next_stationIndex = i+1
                    next_station = stations[i+1]   
                    print("station id "+str(next_station.number))
                    break 
            
        print(current_station)
        #print(current_station.number)
        
        print("station id "+str(station_id))
        #print("station id "+str(next_station.number))
        
        polyindex = Station.objects.get(route=route,index=station_id)
        print("polyindex "+str(polyindex))
        #r_station = Station.objects.filter(route = route,index=station_id).delete()
        #r_polyline = Polyline.objects.filter(route = route,index=polyindex.index).delete()
        #Polyline.objects.filter(route=route,stationIndex=prev_station).delete()
        #if(current_station!=None):
            #Polyline.objects.filter(route=route,stationIndex=current_station).delete()
        nextStation = None    
        try:
            Media.objects.filter(route=route,station_id=polyindex.number).delete()
            print("next station index "+str(next_stationIndex))
            if(next_stationIndex!=-1):
                for i in range(next_stationIndex , len(stations)):
                    print("current station number, index "+str(next_stationIndex)+" "+str(stations[i].number)+" "+str(i)) 
                    media = Media.objects.filter(route=route,station_id=stations[i].number)
                    polyindex = stations[i-1]
                    print("next stations media "+str(len(media))+" "+str(polyindex.number)+"  "+str(stations[i].number))
                    if(len(media)!=0):
                        for m in media:
                            print("next station number "+str(polyindex.number))
                            print(m.as_json())
                            try:
                                print(m.as_json())
                                current_media = m
                                current_media.station_id = polyindex.number
                                eventName = current_media.eventName
                                current_media.eventName = eventName.replace("station"+str(stations[i].number),"station"+str(polyindex.number))
                                nextEventName = current_media.nextEventName
                                if(nextEventName!=None):
                                    current_media.nextEventName = nextEventName.replace("station"+str(stations[i].number),"station"+str(polyindex.number))
                                current_media.save()
                            except ValidationError as e:
                                print(e.args())
                        
        except ValidationError as e:
            print("No Media "+e.args())
            
        response_data['result'] = 'ok'
        response_data['message'] = 'Rutten sparades'
    except ValidationError as e:
        print(e.args())
        
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte ladda rutt från id'
   
    return HttpResponse(json.dumps(response_data), content_type="application/json")


#Delete media that has been uploaded
# @param media_id ID of media
# @param user_id ID of user
def delete_media(media_id, user_id,route_id,station_id,marker_id):
    m = Media.objects.get(id=media_id)
    media = Media.objects.filter(filename=m.filename)
    u = User.objects.get(id=user_id)
    print(m.user)
    print(u)
    
    print(len(media))
    
    #Only delete if you uploaded or if you are admin
    if m.user.id == u.id or u.is_superuser:
        if(len(media)==1):
            os.remove(m.filepath)
        m.delete()
        
    if(station_id==0 and marker_id==0):
        resetStartMediaEventNames(route_id,user_id)
        
    if(station_id!=0):
        resetStationEvents_nextEvents(route_id,u,station_id)
        
    if(marker_id!=0):    
        resetMarkerEvents_nextEvents(route_id,u,marker_id)
            
            #===================================================================
            # index=0
            # for marker_object in markers:
            #     if(marker_object.id == m.id and marker_object.id!=markers[0].id):
            #         if(index!=len(markers)-1):
            #             markers[index-1].nextEventName = markers[index+1].eventName
            #             if(index+2<len(markers)):
            #                 markers[index+1].nextEventName = markers[index+2].eventName
            #             else:
            #                 markers[index+1].nextEventName = None
            #             markers[index-1].save()
            #             markers[index+1].save()
            #             break
            #         else:
            #             markers[index-1].nextEventName = None
            #             markers[index-1].save()
            #             break
            #         
            #         
            #     index+=1           
            #===================================================================

        
        return True
    else:
        return False

def resetStartMediaEventNames(route_id,user_id):
    if(route_id!=0):
        start_media = Media.objects.filter(route_id=route_id,user_id=user_id,mediatype=Media.STARTMEDIA)
        print(route_id)
        print(user_id)
        print(start_media)
        if(len(start_media)>1):
            initial_start_media = start_media[0]
            if(isImageFile(initial_start_media.filename)):
                    initial_start_media.eventName = "start_Image"+str(1)
                    initial_start_media.save()
                    
                     
            if(isAudioFile(initial_start_media.filename)):
                initial_start_media.eventName = "start_Audio"+str(1)
                initial_start_media.save()
                     
            if(isVideoFile(initial_start_media.filename)):
                    initial_start_media.eventName = "start_Video"+str(1)
                    initial_start_media.save()    
             
             
            for i in range(1,len(start_media)-1):
                    #current start media and prev start media
                    curr_start_media = start_media[i]
                    prev_start_media = start_media[i-1]
                    if(isImageFile(curr_start_media.filename)):
                        curr_start_media.eventName = "start_Image"+str(i+1)
                        prev_start_media.nextEventName = "start_Image"+str(i+1)
                        prev_start_media.save()
                        curr_start_media.save()
                         
                    if(isAudioFile(curr_start_media.filename)):
                        curr_start_media.eventName = "start"+"_Audio"+str(i+1)
                        prev_start_media.nextEventName = "start"+"_Audio"+str(i+1)
                        prev_start_media.save()
                        curr_start_media.save()
                         
                    if(isVideoFile(curr_start_media.filename)):
                        curr_start_media.eventName = "start"+"_Video"+str(i+1)
                        prev_start_media.nextEventName = "start"+"_Video"+str(i+1)
                        prev_start_media.save()
                        curr_start_media.save()
             
            curr_start_media = start_media[len(start_media)-1]
            prev_start_media = start_media[len(start_media)-2]     
            if(isImageFile(curr_start_media.filename)):
                    curr_start_media.eventName = "start"+"_Image"+str(len(start_media))
                    prev_start_media.nextEventName = "start"+"_Image"+str(len(start_media))
                    curr_start_media.nextEventName = None
                    prev_start_media.save()
                    curr_start_media.save()
                     
            if(isAudioFile(curr_start_media.filename)):
                    curr_start_media.eventName = "start"+"_Audio"+str(len(start_media))
                    prev_start_media.nextEventName = "start"+"_Audio"+str(len(start_media))
                    curr_start_media.nextEventName = None
                    prev_start_media.save()
                    curr_start_media.save()
                     
            if(isVideoFile(curr_start_media.filename)):
                    curr_start_media.eventName = "start"+"_Video"+str(len(start_media))
                    prev_start_media.nextEventName = "start"+"_Video"+str(len(start_media))
                    curr_start_media.nextEventName = None
                    prev_start_media.save()
                    curr_start_media.save()    
                     
            elif(len(start_media)==1):
                last_start_media = start_media[0] 
                if(isImageFile(last_start_media.filename)):
                    last_start_media.eventName = "start"+"_Image"+str(1)
                    last_start_media.nextEventName= None
                    last_start_media.save()
                     
                if(isAudioFile(last_start_media.filename)):
                    last_start_media.eventName = "start"+"_Audio"+str(1)
                    last_start_media.nextEventName= None
                    last_start_media.save()
                     
                if(isVideoFile(last_start_media.filename)):
                    last_start_media.eventName = "start"+"_Video"+str(1)
                    last_start_media.nextEventName= None
                    last_start_media.save()

            
        
        

def resetMarkerEvents_nextEvents(route_id,u,marker_id):
    if(marker_id!=0):
            marker = Marker.objects.filter(route_id =route_id,index = marker_id) 
            markers = Media.objects.filter(marker=marker[0],user=u)
            if(len(markers)>1):
                if(isImageFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Image"+str(1)
                    markers[0].save()
                    
                if(isAudioFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Audio"+str(1)
                    markers[0].save()
                    
                if(isVideoFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Video"+str(1)
                    markers[0].save()    
            
            
                for i in range(1,len(markers)-1):
                    if(isImageFile(markers[i].filename)):
                        markers[i].eventName = "marker"+str(marker_id)+"_Image"+str(i+1)
                        markers[i-1].nextEventName = "marker"+str(marker_id)+"_Image"+str(i+1)
                        markers[i-1].save()
                        markers[i].save()
                        
                    if(isAudioFile(markers[i].filename)):
                        markers[i].eventName = "marker"+str(marker_id)+"_Audio"+str(i+1)
                        markers[i-1].nextEventName = "marker"+str(marker_id)+"_Audio"+str(i+1)
                        markers[i-1].save()
                        markers[i].save()
                        
                    if(isVideoFile(markers[i].filename)):
                        markers[i].eventName = "marker"+str(marker_id)+"_Video"+str(i+1)
                        markers[i-1].nextEventName = "marker"+str(marker_id)+"_Video"+str(i+1)
                        markers[i-1].save()
                        markers[i].save()
            
                    
                if(isImageFile(markers[len(markers)-1].filename)):
                    markers[len(markers)-1].eventName = "marker"+str(marker_id)+"_Image"+str(len(markers))
                    markers[len(markers)-2].nextEventName = "marker"+str(marker_id)+"_Image"+str(len(markers))
                    markers[len(markers)-1].nextEventName = None
                    markers[len(markers)-2].save()
                    markers[len(markers)-1].save()
                    
                if(isAudioFile(markers[len(markers)-1].filename)):
                    markers[len(markers)-1].eventName = "marker"+str(marker_id)+"_Audio"+str(len(markers))
                    markers[len(markers)-2].nextEventName = "marker"+str(marker_id)+"_Audio"+str(len(markers))
                    markers[len(markers)-1].nextEventName = None
                    markers[len(markers)-2].save()
                    markers[len(markers)-1].save()
                    
                if(isVideoFile(markers[len(markers)-1].filename)):
                    markers[len(markers)-1].eventName = "marker"+str(marker_id)+"_Video"+str(len(markers))
                    markers[len(markers)-2].nextEventName = "marker"+str(marker_id)+"_Video"+str(len(markers))
                    markers[len(markers)-1].nextEventName = None
                    markers[len(markers)-2].save()
                    markers[len(markers)-1].save()    
                    
            elif(len(markers)==1):
                if(isImageFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Image"+str(1)
                    markers[0].nextEventName= None
                    markers[0].save()
                    
                if(isAudioFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Audio"+str(1)
                    markers[0].nextEventName= None
                    markers[0].save()
                    
                if(isVideoFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Video"+str(1)
                    markers[0].nextEventName= None
                    markers[0].save()
    
def resetStationEvents_nextEvents(route_id,u,station_id):
    if(station_id!=0):
            stations = Station.objects.filter(route_id =route_id,id = station_id) 
            station_media = Media.objects.filter(station=stations[0],user=u)
            station_index = stations[0].number
            if(len(station_media)>1):
                if(isImageFile(station_media[0].filename)):
                    station_media[0].eventName = "station"+str(station_index)+"_Image"+str(1)
                    station_media[0].save()
                    
                if(isAudioFile(station_media[0].filename)):
                    station_media[0].eventName = "station"+str(station_index)+"_Audio"+str(1)
                    station_media[0].save()
                    
                if(isVideoFile(station_media[0].filename)):
                    station_media[0].eventName = "station"+str(station_index)+"_Video"+str(1)
                    station_media[0].save()    
            
            
                for i in range(1,len(station_media)-1):
                    if(isImageFile(station_media[i].filename)):
                        station_media[i].eventName = "station"+str(station_index)+"_Image"+str(i+1)
                        station_media[i-1].nextEventName = "station"+str(station_index)+"_Image"+str(i+1)
                        station_media[i-1].save()
                        station_media[i].save()
                        
                    if(isAudioFile(station_media[i].filename)):
                        station_media[i].eventName = "station"+str(station_index)+"_Audio"+str(i+1)
                        station_media[i-1].nextEventName = "station"+str(station_index)+"_Audio"+str(i+1)
                        station_media[i-1].save()
                        station_media[i].save()
                        
                    if(isVideoFile(station_media[i].filename)):
                        station_media[i].eventName = "station"+str(station_index)+"_Video"+str(i+1)
                        station_media[i-1].nextEventName = "station"+str(station_index)+"_Video"+str(i+1)
                        station_media[i-1].save()
                        station_media[i].save()
            
                    
                if(isImageFile(station_media[len(station_media)-1].filename)):
                    station_media[len(station_media)-1].eventName = "station"+str(station_index)+"_Image"+str(len(station_media))
                    station_media[len(station_media)-2].nextEventName = "station"+str(station_index)+"_Image"+str(len(station_media))
                    station_media[len(station_media)-1].nextEventName = None
                    station_media[len(station_media)-2].save()
                    station_media[len(station_media)-1].save()
                    
                if(isAudioFile(station_media[len(station_media)-1].filename)):
                    station_media[len(station_media)-1].eventName = "station"+str(station_index)+"_Audio"+str(len(station_media))
                    station_media[len(station_media)-2].nextEventName = "station"+str(station_index)+"_Audio"+str(len(station_media))
                    station_media[len(station_media)-1].nextEventName = None
                    station_media[len(station_media)-2].save()
                    station_media[len(station_media)-1].save()
                    
                if(isVideoFile(station_media[len(station_media)-1].filename)):
                    station_media[len(station_media)-1].eventName = "station"+str(station_index)+"_Video"+str(len(station_media))
                    station_media[len(station_media)-2].nextEventName = "station"+str(station_index)+"_Video"+str(len(station_media))
                    station_media[len(station_media)-1].nextEventName = None
                    station_media[len(station_media)-2].save()
                    station_media[len(station_media)-1].save()    
                    
            elif(len(station_media)==1):
                if(isImageFile(station_media[0].filename)):
                    station_media[0].eventName = "station"+str(station_index)+"_Image"+str(1)
                    station_media[0].nextEventName= None
                    station_media[0].save()
                    
                if(isAudioFile(station_media[0].filename)):
                    station_media[0].eventName = "station"+str(station_index)+"_Audio"+str(1)
                    station_media[0].nextEventName= None
                    station_media[0].save()
                    
                if(isVideoFile(station_media[0].filename)):
                    station_media[0].eventName = "station"+str(station_index)+"_Video"+str(1)
                    station_media[0].nextEventName= None
                    station_media[0].save()
    



#Check if route exist or you own it
#Superuser always return the route if it exist
def validateRoute(route_id, user):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return False
    if not user.is_superuser:
        if route.user != user:
            return False

    return route
