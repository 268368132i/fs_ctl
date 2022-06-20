from .models import Asset, Settings
from .ctl import *
import re
def play(request, conf_ext):
    file_path = Asset.objects.get(pk=request.POST.get('fileId')).fileField.path
    fullScreen = request.POST.get('fullScreen')
    conf_action("stop", conf_ext)
    return response_to_json(conf_action("play {vol=-10}" + file_path, conf_ext))

def stop(request, conf_ext):
    return response_to_json(conf_action("stop", conf_ext))

def tpause(request, conf_ext):
    return response_to_json(conf_action("pause_play", conf_ext))

def logo_on(request, conf_ext):
    opts = Settings.objects.get(name='logo_params').data    
    path = Settings.objects.get(name='logo_path').data
    text = request.POST.get('text')
    alt_text = request.POST.get('alt_text')
    if len(alt_text)==0:
      opts=re.sub(r',alt_text=.*:<alt_text>','',opts)
    opts = opts.replace('<alt_text>','\'' + alt_text + '\'')
    print('alt_text=' + alt_text)
    opts = opts.replace('<text>', '\''+text+'\'')
    participant_num = request.POST.get('participant_num')
    action = 'vid-logo-img ' + participant_num + ' {' + opts + '}' + path
    
    return response_to_json(conf_action(action, conf_ext))
  
def banner_off(request, conf_ext):
    participant_num = request.POST.get('participant_num')
    action = 'vid-banner ' + participant_num + ' clear'
    return response_to_json(conf_action(action, conf_ext))

def banner_on(request, conf_ext):
    participant_num = request.POST.get('participant_num')
    text = request.POST.get('text')
    opts = Settings.objects.get(name='banner_opts').data
    action = 'vid-banner ' + participant_num + ' {' + opts + '}' + text
    return response_to_json(conf_action(action, conf_ext))

def processor(request, conf_ext):
    commands = {'play': play,
                'stop': stop,
                'tpause': tpause,
                'logo_on': logo_on,
                'banner_off': banner_off,
                'banner_on': banner_on,
                }
    confinfo = ''
    command_response = ''
    action = request.POST.get('action')
    if action not in commands:
        return {'success':False, 'comment': 'Command not found.'}    
    command_response = commands[action](request, conf_ext)
    if request.POST.__contains__('refresh') and request.POST.get('refresh')==True:
        confinfo = conf_json_info(conf_ext)
        return {**actresp, **confinfo}    
    return command_response
