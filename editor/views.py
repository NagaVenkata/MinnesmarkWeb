import json
import os
import decimal
from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.exceptions import ValidationError,NON_FIELD_ERRORS
from editor import models
import editor
import imghdr
import sndhdr
from editor.models import Media, Route, Station, Polyline, Marker
from minnesmark.settings import PROJECT_ROOT
from editor.jsonObject import TitleEvents
from editor.jsonObject import Station_SwingPointEvents,MarkerEvent,MediaEvent

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
                print(request.user.username)
                print(request.user.id)
                print(request.FILES['media_file'])
                print(route_id)
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
                                   'cur_route':route,
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
            
            
    
    print("entered")

    if route.user == request.user or request.user.is_superuser:
        
        if request.is_ajax():
            print("ajax request")
            print(request.GET['id'])
            print(request.GET['type'])
            marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
            media_object = Media.objects.filter(id=request.GET['id'],route=route,marker=marker_object[0])
            media = media_object[0]
            print(media.options)
            print(media.id)
            try:
                print(Media.PANORAMA)           
                media.options = request.GET['type']
                media.save()
                media_object = Media.objects.filter(id=request.GET['id'],route=route,marker=marker_object[0])
                print(media_object[0].options)
            except ValidationError as e:
                print(e.args)

        
        #stations = Station.objects.filter(route=route)
        marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
        if(len(marker_object)==0):
            save_marker_to_database(request,route_id,marker_id)
        if(request.method == 'POST'):
            try:
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
        print(marker_media[len(marker_media)-1]['options'])
        #print(marker_media)
        return render_to_response('editor/markerMediaPage.html',
                                  {'marker_media':marker_media,
                                   'routes': routes,
                                   'cur_route':route,
                                   'marker_id':markerName,
                                   'prev_media_type':marker_media[1]['options']
                                   },
                              context_instance=RequestContext(request))
    else:
        redirect('/account/login')
        
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
                            name = "Marker"+str(marker_id),
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
        publish_trail(request,route_id)

    #Get all media set to startmedia
    start_media = []
    for m in Media.objects.filter(route=route,mediatype=Media.STARTMEDIA, user=request.user).order_by('order'):
        start_media.append(m.as_json())
    return render_to_response('editor/publish.html', {'routes': routes,'cur_route':route_id,'start_media':start_media},
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
    
    title.writeEvent("NumberOfRegions","numRegions", len(stations))
    attrib.append(title.asJson())
    
    #attrib.append(attr)
    #attrib.append(attr1)
    station = Station_SwingPointEvents(route)
    for p in points:
        station.PolylineIndex(p)
        attrib.append(station.as_json())
    
    markerEvent = MarkerEvent(route)
    
    for marker in markers:
        marker_media = Media.objects.filter(route=route,marker=marker)
        if(len(marker_media)!=0):
            markerEvent.markersIndex(marker,marker_media[0])
            attrib.append(markerEvent.as_json())
            
    for marker in markers:
        marker_media = Media.objects.filter(route=route,marker=marker)
        if(len(marker_media)!=0):
            for media in marker_media:
                mediaEvent = MediaEvent(media)
                mediaEvent.mediaIndex(media)
                attrib.append(mediaEvent.as_json())
                
           
    
    print(json.dumps(attrib))
    
    path = PROJECT_ROOT
    os.chdir(path)
    # Move up one
    os.chdir('..')
    #Enter user folder
    #os.chdir('users/')
    #folder = os.getcwd()

    try:
        #if User hasen't uploaded anything yet, create folder
        os.mkdir("json" + '/')
    except:
        pass

    #change to user folder
    os.chdir("json")
    folder = os.getcwd()

    #Fullpath to file
    fullpath = folder + "/" + "tex.json"
    
    

    #Try to create file
    try:
        with open(fullpath, 'w') as f:
            json.dump(attrib, f,sort_keys = True, indent = 4, ensure_ascii=True)
    except:
        return False
    
    
    
# /editor/media/<route_id>/station/<station_id>
# NOT DONE IN URL !!!!!
# TODO render right media with files
@login_required
def render_page_addMedia(request,route_id):
    routes = get_all_routes_from_user(request.user.id)
    print(request)
    return render_to_response('editor/addMedia.html', {'routes': routes,'cur_route':route_id},
                               context_instance=RequestContext(request))

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
    folder = os.getcwd()

    #Fullpath to file
    fullpath = folder + "/" + f.name
    
    

    #Try to create file
    try:
        with open(fullpath, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    except:
        return False

    
    userobject = User.objects.get(id=request.user.id)
    route_object = Route.objects.get(id=route_id)
    
    if(marker_id!=0):
        marker_object = Marker.objects.filter(route_id=route_id,index=marker_id)
    
    media_count = 0
    
    if(station_id == 0 and marker_id == 0):
        media_count = Media.objects.filter(mediatype=Media.STARTMEDIA, user=userobject).count()
    
    if(marker_id!=0):
        media_count = Media.objects.filter(marker=marker_object[0],mediatype=Media.AR_MEDIA, user=userobject).count()
        markers = Media.objects.filter(marker=marker_object[0],mediatype=Media.AR_MEDIA, user=userobject)
        
    print(route_object)    
    print(marker_object[0])
    
    type=None
        
        
        
    media = None  
    eventName = None  
    
    if(station_id == 0 and marker_id == 0):
        #Save media as STARTMEDIA
        # TODO create any type of media and add to station
        eventName = f.name+str(media_count+1)
        media = Media(route=route_object,
                filename=f.name,
                filepath=fullpath,
                size=f.size,
                treasure=False,
                mediatype=Media.STARTMEDIA,
                user=userobject,
                order=media_count + 1,
                station=None,
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
        
        
        
        if(isImageFile(f.name)):
            eventName = "marker"+str(marker_id)+"_"+"Image"+str(media_count+1)
            type="image"
        if(isAudioFile(f.name)):
            eventName = "marker"+str(marker_id)+"_"+"Audio"+str(media_count+1)
            type="audio"
        if(isVideoFile(f.name)):
            eventName = "marker"+str(marker_id)+"_"+"Video"+str(media_count+1)
            type="video"    
        
            
        
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
                station=None,
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
    fileExt = imghdr.what(fileName) 
    
    if(fileExt == "jpg" or fileExt == "JPG" or fileExt == "jpeg" or fileExt == "JPEG" or fileExt == "png" or fileExt == "PNG"  or fileExt == "bmp" or fileExt == "BMP" or fileExt == "gif" or fileExt == "GIF"):
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

        for s in json_obj["stations"]:
            station = Station(route=route,
                              number=s["number"],
                              index=s["index"])
            station.save()
    except:
        response_data['result'] = 'failed'
        response_data['message'] = 'Kunde inte spara markörer'
    #Save positoins on polyline
    try:
        for point in json_obj["points"]:
            point = Polyline(route=route,
                           latitude=point["latitude"],
                           longitude=point["longitude"],
                           index=point["index"],
                           radius = point["radius"],
                           shouldDisplayOnCompass = point["shouldDisplayOnCompass"],
                           swingPoint = point["swingPoint"])
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
        route.name = json_obj['name'];
        route.save()
        response_data['result'] = 'ok'
        response_data['message'] = 'Sparat'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data['result'] = 'failed'
        response_data['message'] = 'Du äger inte denna rutt.'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

#Delete media that has been uploaded
# @param media_id ID of media
# @param user_id ID of user
def delete_media(media_id, user_id,route_id,station_id,marker_id):
    m = Media.objects.get(id=media_id)
    u = User.objects.get(id=user_id)
    print(m.user)
    print(u)
    
    
    
    #Only delete if you uploaded or if you are admin
    if m.user.id == u.id or u.is_superuser:
        os.remove(m.filepath)
        m.delete()
        
        
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
                    markers[0].save()
                    
                if(isAudioFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Audio"+str(1)
                    markers[0].save()
                    
                if(isVideoFile(markers[0].filename)):
                    markers[0].eventName = "marker"+str(marker_id)+"_Video"+str(1)
                    markers[0].save()
                    
                    
                
                
            
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