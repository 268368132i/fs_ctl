fsServer="your_freeswitch_domain"
fsPasswd="ws_password"

def getFSSocket():
        return "wss://" + fsServer + ":443/socket/"
