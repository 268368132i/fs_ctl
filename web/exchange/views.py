from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.http import HttpResponse,HttpResponseRedirect
from .models import (
                     ConfAuth, Assignment, 
                     Conference, ConfUser,
                     ConfFlags, ParamsCache, 
                     Settings,Asset, Recording,
                     )
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

import hashlib
from .vars import *
from .ctl import *
from .proc_commands import processor
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout

#Text manipulations
from re import sub

#Generate record file name
from datetime import datetime
from time import sleep

#Needed for directory listing
from glob import iglob
from os.path import basename,getsize

serverSecret='2fdvg56'

def getConf(request):
  key = request.GET.get('key')
  candidates = ConfAuth.objects.filter(key=key)
  if candidates.count()>0:
    auth = candidates.first()
    userName=auth.userName
    response = JsonResponse({
    'key': key,
    'user': userName,
    'permissions': 'view',
    'confName': auth.confName,
    'confDescription': auth.confDescription,
    'confExt': auth.confExt,
    })
  else:
    response = JsonResponse({
    'key': 'key not found',
    })
  return response
    
def confs(request):
  authed = request.user.is_authenticated
  if authed:
    user = ConfUser.objects.filter(registered_user=request.user).first()
    key = user.key
  else:
    key = request.GET.get('key')
    #Some registered participants may have an empty 'key' (like those connecting with hardware endpoints)
    if key is not None and len(key)>0:
      user = ConfUser.objects.filter(key=key).first()
    else:
      user = None
  if user is None and key is None:
    return redirect('accounts:user_login')
  assignments = Assignment.objects.filter(user=user)
  for assignment in assignments:
    str2hash=str(assignment.id) + assignment.user.key + serverSecret
    assignment.hash = hashlib.md5(str2hash.encode()).hexdigest()
    connected_users = get_conf_users(str(assignment.conference.extension))
    assignment.num_connected = len(connected_users)
    assignment.user_list=connected_users
  
  context = {
    'title': "Список доступных конференций",
    'assignments': assignments,
    'key': key,
    'total_assignments': len(assignments),
    'user':user,
    'authenticated': authed,
  }
  return render(request, 'listConfs.html', context=context)
  
def tokenize(request):
  return HttpResponse(" ")

@login_required
def confControl(request, uuid):
  #action = request.GET.get('action')
  #uuid = request.GET.get('uuid')
  #csum = request.GET.get('csum')
  ass = Assignment.objects.get(pk=uuid)
  #if ass.count()==0:
  #  return HttpResponse(" ")
  #ass=ass.first()
  str2hash=str(ass.id)+ass.user.key+serverSecret
  #if hashlib.md5(str2hash.encode()).hexdigest()!=csum or not request.user.is_authenticated:
  if ass.user.registered_user.id != request.user.id or ass.flags.name != 'admin':
    return HttpResponse("Auth. error 1: " + str(ass.user.registered_user.id) + '  ' + str(request.user.id) + '  ' + str(ass.flags.name))
  if request.method !='POST' or not request.is_ajax():
    return HttpResponse("Format error")
  
  conf_ext=ass.conference.extension
  
  action = request.POST.get('action')
  args = request.POST.get('args')
  
  print("ConfControl(ctl) - action: " + str(action) + "; args: " + str(args))
  if action == 'end':
    return JsonResponse(response_to_json(kick_all(conf_ext)))
  elif action=='conf-info':
    return JsonResponse(conf_json_info(conf_ext))
  elif action=='vid-logo':
    action='vid-logo-img'
    participant_num = request.POST.get('participant_num')
    text = request.POST.get('text')
    return JsonResponse(response_to_json(logo_on(
      opts=Settings.objects.get(name='logo_params').data,
      img_path=Settings.objects.get(name='logo_path').data,
      participant_num=participant_num,
      text=text)))
  else:
    if action=='record':
      now = datetime.now()
      fn = now.strftime('%Y%m%d_%H%M%S')
      path = ctl_get_raw_conf_recordings_path(conf_ext)
      full_fn = path + fn
      file_format = Settings.objects.get(name='record_file_format').data
      action  = "record" + " " + full_fn + "." + file_format
    actresp = response_to_json(conf_action(action, conf_ext))
    sleep(2)
    confinfo = conf_json_info(conf_ext)
    return JsonResponse({**actresp, **confinfo})
  
def ctl_get_raw_conf_recordings_path(conf_ext):
  return Settings.objects.get(name='record_path').data + conf_ext + '/'

@login_required
def conf_ctl_page(request, assignment_id):
  assignment = Assignment.objects.get(pk=assignment_id)
  conf_user = assignment.user
  if conf_user.registered_user.pk != request.user.pk or assignment.flags.name != 'admin':
      return HttpResponse("Auth. error")
  layouts = ParamsCache.objects.filter(name="layouts")
  if len(layouts)<1:
      layouts_cache = ParamsCache.objects.create(name="layouts")
      layouts_cache.data = conf_action("vid-layout list", assignment.conference.extension)
      layouts_cache.save()
  else:
      layouts_cache = layouts.first()
  context = {
      'assignment':assignment,
      'layouts':layouts_cache.data.split('\n')
      }
  return render(request, 'exchange/ctl_page.html', context=context)

@login_required
def new_ctl(request, uuid):
    ass = Assignment.objects.get(pk=uuid)
    if ass.user.registered_user.id != request.user.id or ass.flags.name != 'admin':
        return HttpResponse("Auth. error 1: " + str(ass.user.registered_user.id) + '  ' + str(request.user.id) + '  ' + str(ass.flags.name))
    
    conf_ext=ass.conference.extension
    return JsonResponse(processor(request, conf_ext))

def recordings(request, conf):
  conf = Conference.objects.get(pk=conf) 
  #List published files
  created = Recording.objects.filter(conference=conf)
  published = created.filter(status__gt=4)
  ctx = {
    'conference': conf,
    'published': published,
    }
  #Raw files
  if request.user.is_authenticated:
    ass = Assignment.objects.filter(conference = conf).filter(user = ConfUser.objects.get(registered_user=request.user)).filter(flags=ConfFlags.objects.get(name='admin')).first()
    print('Authenticated user has flags: ' + str(ass.flags.name))
    if ass:
      
      in_process = created.filter(status__lt=5)
      
      ctx['is_admin'] = True
      file_format = Settings.objects.get(name='record_file_format').data
      fng = ctl_get_raw_conf_recordings_path(conf.extension) + '*.' + file_format
      print("All raw files by: " + fng)
      raw = []
      dtm = None
      for f in iglob(ctl_get_raw_conf_recordings_path(conf.extension) + '*.' + file_format):
        fn = basename(f)
        try:
          dtm = datetime.strptime(fn.replace("." + file_format,""),'%Y%m%d_%H%M%S')
        except ValueError as e:
          print(e)
          continue
        raw.append({'file_name':fn, 'date_time': dtm})
      ctx['raw'] = raw
      ctx['in_process'] = in_process
      
  return render(request, 'exchange/recordings.html', context=ctx)

def is_conf_admin(user, conference):
  conf_user = ConfUser.objects.get(registered_user=user)
  admin_flags = ConfFlags.objects.get(name='admin')
  return Assignment.objects.filter(conference=conference, user=conf_user, flags=admin_flags).exists()

def get_recording(request, conf, file_name, published):
  conf = Conference.objects.get(pk=conf)
  file_format = Settings.objects.get(name='record_file_format').data
  processed_dir = {1 : "published", 0 : "raw"}
  if True:
    #size = getsize(ctl_get_raw_conf_recordings_path(conf.extension) + file_name)
    response = HttpResponse()
    response['Content-Type']='video/' + file_format
    #response['Content-Length'] = size
    #response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
    response['Accept-Ranges'] = 'bytes'
    response['Content-Encoding'] = ''
    response["X-Accel-Redirect"] = '/recordings/{2}/{0}/{1}'.format(conf.extension, file_name, processed_dir[published])
    return response
  
class PublishRecordingView(LoginRequiredMixin, CreateView):
  model = Recording
  fields = ['fname', 'conference','name', 'description', 'startDate'] 
  initial = {'status':1}

  def get_form(self):
    form = super().get_form()
    
    form.fields['fname'].disabled=True
    form.fields['fname'].initial=self.kwargs['file_name']
    
    start_date = sub('\..{3,4}$','',self.kwargs['file_name'])
    start_date = datetime.strptime(start_date,'%Y%m%d_%H%M%S')
    form.fields['startDate'].disabled=True
    form.fields['startDate'].initial=start_date
    
    form.fields['conference'].disabled=True
    form.fields['conference'].initial=self.kwargs['conf']    
    return form
  
  def form_valid(self, form):    
    form.instance.status = 1
    return super().form_valid(form)
  
  def get_success_url(self):
    return reverse('exchange:recordings', kwargs={'conf':self.kwargs['conf']})
  
class UpdateRecordingView(LoginRequiredMixin, UpdateView):
  model = Recording
  fields = ['fname','conference','name', 'description', 'startDate']
  def get_form(self):
    form = super().get_form()
    form.fields['fname'].disabled=True
    form.fields['startDate'].disabled=True
    form.fields['conference'].disabled=True
    return form
  def get_success_url(self):
    return reverse('exchange:recordings', kwargs={'conf':self.get_object().conference.pk})
  
class DeletePublishedRecordingView(LoginRequiredMixin, DeleteView):
  model = Recording
  def delete(self, request, *args, **kwargs):
    obj = self.get_object()
    conf = obj.conference
    if is_conf_admin(request.user, conf):
      return super().delete(request, *args, **kwargs)
    else:
      return Http404('File not found')
  def get_success_url(self):
    return reverse('exchange:recordings', kwargs={'conf': self.object.conference.pk})
      
  

  

class UploadAssetView(LoginRequiredMixin,CreateView):
    model = Asset
    fields = ['name', 'fileField','conference']
    context_name = 'asset'
    def form_valid(self, form):
        print("setting user")
        form.instance.user = self.request.user
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('exchange:list_assets', kwargs={'conf': self.object.conference.pk},)
    
class DeleteAssetView(LoginRequiredMixin, DeleteView):
    model = Asset
    context_name = 'asset'
    def get_success_url(self):
        return reverse('exchange:list_assets', kwargs={'conf': self.object.conference.pk})
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == request.user:
            return super(DeleteAssetView, self).delete(request, *args, **kwargs)
        else:
            return Http404('File not found')
    
class AssetsListView(LoginRequiredMixin, ListView):
    model = Asset    
    def get_queryset(self):
        self.conf = Conference.objects.get(pk=self.kwargs['conf'])        
        return Asset.objects.filter(conference=self.conf).filter(user=self.request.user)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conference'] = self.conf
        confUser = ConfUser.objects.filter(registered_user=self.request.user).first()
        ass = Assignment.objects.filter(conference=self.conf).filter(user=confUser).filter(flags=ConfFlags.objects.get(name='admin')).first()
        context['assignment'] = ass
        return context
    
  

def connect(request):
  uuid = request.GET.get('uuid')
  csum = request.GET.get('csum')
  screenshare_only = request.GET.get('cshare')
  ass = Assignment.objects.filter(id=uuid)
  if ass.count()==0:
    return HttpResponse(" ")
  else:
    ass=ass.first()
    str2hash=str(ass.id)+ass.user.key+serverSecret
    if hashlib.md5(str2hash.encode()).hexdigest()!=csum:
      return HttpResponse("Auth. error")
  username = ass.user.name
  confExt = ass.conference.extension
  confName = ass.conference.name
  confDescr = ass.conference.description
  flagsName = ass.flags.name
  
  #
  if flagsName == 'screenshare':
      dev = 'none'
      skip_check = "true"
      screenshare_only = True
  elif flagsName == "viewer":
      dev = 'none'
      skip_check = "true"
      screenshare_only = False
  else:
      dev = 'any'
      skip_check = "false"
      screenshare_only = False
  
  context = {
    'username' : username,
    'confExt' : confExt,
    'confName' : confName,
    'confDescr' : confDescr,
    'flagsName' : flagsName,
    'FSSocket':getFSSocket(),
    'FSLogin':"1008@"+fsServer,
    'FSPasswd':fsPasswd,
    'uuid' : uuid,
    'screenshare_only': screenshare_only,
    'cshare' : screenshare_only,
    'dev' : dev,
    'skip_check' : skip_check,
  }
  
  return render(request, 'connect.html', context=context)
# Create your views here.
