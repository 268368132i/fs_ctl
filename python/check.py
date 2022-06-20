#coding=utf-8
import pymysql.cursors
from freeswitch import *

connection=pymysql.connect(
  host = "localhost",
  user = "dbuser",
  password = "passwd",
  db="verto",
  charset='utf8mb4',
  cursorclass=pymysql.cursors.DictCursor
)



def handler(session,args):
  print(session)

def fsapi(session, stream, env, args):
  fontFace="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
  uuid=session.getVariable("verto_dvar_uuid")
  accCode=session.getVariable("accountcode")
  csum=session.getVariable("verto_dvar_csum")

#Check if screenshare
  is_screen = session.getVariable("video_screen_share")
  consoleLog( "info", "is screen: %s " % is_screen)
  
#Destination for verto users is different from the one for sip users  
  conf=session.getVariable("verto_remote_caller_id_number")
  if conf is None:
    conf = session.getVariable("sip_to_user")

#Screenshare gets its own settings
  if is_screen == "true":      
      conf=conf.replace("-screen","")
      consoleLog( "info", "replacing conf: %s " % conf)

  ip = session.getVariable("sip_network_ip")
  if uuid:
    uuid=uuid.replace("-","")

  try:
    with connection.cursor() as cursor:
#This request needs to be rewritten: all string vars should be parameters
      sql = "SELECT exchange_confuser.name as `username`, flags FROM exchange_assignment JOIN exchange_conference ON exchange_conference.`id`=exchange_assignment.conference_id JOIN exchange_confflags ON exchange_confflags.id=exchange_assignment.flags_id JOIN exchange_confuser ON exchange_confuser.id = exchange_assignment.user_id WHERE (exchange_assignment.id='" + str(uuid) + "' AND `extension` LIKE '" + str(conf) + "') OR (exchange_confuser.ip LIKE '" + str(ip) + "' AND `extension` LIKE '" + str(conf) + "')"
      consoleLog( "info", "SQL: %s " % sql)
      n=cursor.execute(sql)
      session.execute("set","got_results=" + str(n))
#If we got at least one match then we set the user as authenticated
      if n>0:
        res=cursor.fetchone()
        session.execute("set","conf_flags=" + str(res["flags"]))
        userName = res["username"].encode('utf8')
        if is_screen == "true":
          userName += "-screen"
        else:
#Set banner text with user's name
          session.execute("set","video_banner_text={font_face=" + fontFace + ",font_scale=4,bg=#192188,fg=#FFFFFF,min_font_size=6,max_font_size=12}" + userName)
        session.execute("set","ext_authenticated=true")
        consoleLog("info", "Setting call_id_name to: %s " % userName)
        session.execute("set","caller_id_name=" + userName)
        

      else:
        session.execute("set","ext_authenticated=false")

  finally:
    connection.close()
  session.execute("set","verto_dvar_key=OK")
  if session.getVariable("verto_dvar_key")=="3ttd":
    stream.write("true")
  else:
    stream.write("false")
  
