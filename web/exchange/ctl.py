import socket
import sys
from time import sleep
import re
import json

def send_request(request):
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = '/tmp/socket_test.s'
    print('connecting to {}'.format(server_address))
    try:
            sock.connect(server_address)
    except socket.error as msg:
            print(msg)
            sys.exit(1)
    try:
        
        # Send data
        request=request.encode('utf-8')
        print('sending {!r}'.format(request))
        sock.sendall(request)

        amount_received = 0
        amount_expected = 20480
        data=''
        while True:
            buf = sock.recv(512)
            sleep(0.2)
            if not buf: break
            amount_received += len(buf)
            data += buf.decode('utf-8')
            print('received {!r}'.format(buf))

    finally:
        print('closing socket')
        sock.close()
    return data

def test():
    r=send_request('list_users').split('\n')
    for line in r:
        print(line)

class ConnectedUser:
    def __init__(self,description):
        self.description=description.split(';')
        
    def getName(self):
        return self.description[3]
    
    def getUUID(self):
        return self.description[2]
    
    def getId(self):
        return self.description[0]
    
    def __str__(self):
        return self.description[3]

def get_conf_users(conf='3622'):
    users=[]
    listing=list_conf(conf).split('\n')
    for i in range(len(listing)-1):
        u=listing[i].split(';')
        if len(u)<4: break
        user={
            'id':u[0],
            'uuid':u[2],
            'name':u[3],
            }
        users.append(user)
    return users

def list_conf(conf='3622'):
    return send_request('conference ' + str(conf) + ' list')

def kick_all(conf='3622'):
    return send_request('conference ' + str(conf) + ' kick all')

def conf_action(action, conf='3622'):
    return send_request('conference ' + str(conf) + ' ' + action)

def conf_json_info(conf='3622'):
    response = send_request('conference ' + str(conf) + ' json_list')
    if re.search('^-ERR',response):
        return response_to_json(response)
    data = json.loads(response)[0]
    print(data)
    return data
  
def logo_on(opts, text, participant_num, img_path, conf='3622'):
    return send_request('conference ' + str(conf) + ' vid-logo-img ' + participant_num + ' {' + opts + ":'" + text + '\'}' + img_path)
    


def response_to_json(response):
    json = {
        'success': True if re.search('^\\+OK',response) else False,
        'comment':re.sub('\\n','',re.sub('^(\\+OK|-ERR) ','',response)),
        }
    return json
