from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import json

data = {'result of http': 'this is a frist test'}
host = ('0.0.0.0', 8888)

last_authority = {}
last_instruction_time = {}
last_people = {}


a = 'a'

def do_json(data):
    l_instruction = '0'
    l_currentuser = '0'
    l_authoritycompara = '0'
    l_instruction_cover = '0'
    l_light_state = '0'
    l_brightness = '0'
    l_have_people = '0'
    l_nobody_set = '0'
    l_button_set = '0'
    b = parse.parse_qs(data)
    print(b)
    print(type(b))
    data = b


    
    ''' load the room id  '''
    l_rid = json.loads(data['rid'][0].replace("'", '"'))
    l_bid = l_rid['BID']
    l_rid = l_rid['RID']
    rid = str(l_bid) + "-" + str(l_rid)
    l_time = float(data['time'][0])




    ''' sensors '''
    s = json.loads(data['sensors'][0].replace("'", '"'))          
    brightness = 0
    motion = 0
    button = 0
    for i in s:
        if i['data'] == 'offline':
            break
        if i['type'] == 1:
            brightness = brightness | int(i['data']) 
        if i['type'] == 2:
            motion = motion | int(i['data'])
        if i['type'] == 3:
            button = button | int(i['data'])
    '''devices'''
    d = json.loads(data['sensors'][0].replace("'", '"'))
    light = 0
    for i in d:
        if i['data'] == 'offline':
            break
        if i['type'] == 0:
            light = light | int(i['data'])


    ''' set the parameter '''

    l_currentuser = data['authority'][0]      #0 no cmd  1 student 2teacher
    l_instruction = data['cmd'][0]

    # check the authority
    if rid not in last_authority.keys():
        last_authority[rid] = 1
    if l_currentuser > last_authority[rid]:
        l_authoritycompara = '1'
    # check the time
    l_nowtime = float(data['time'][0])
    if rid not in last_instruction_time.keys():
        last_instruction_time[rid] = 0.0
    if l_nowtime - last_instruction_time > 60:
        l_instruction_cover = 1
    l_light_state = str(light)
    l_brightness = str(brightness)
    l_have_people = str(motion)
    if rid not in last_people.keys():
        last_people[rid] = 0.0
    if motion:
        last_people[rid] = l_nowtime
    if motion == 0 and l_nowtime - last_people[rid] > 120:
        l_nobody_set = '1'
    l_button_set = str(button)

    '''
    last_authority = {bid-rid: 1/2}
last_instruction_time = {bid-rid: time}
last_people = {bid-rid: time(last motion == 1)}

string list =["instruction:0/1   off/on", "currentuser:0/1/2  xintiao/stu/teacher", "authoritycompara: 0/1  now<= last_authority(first 1)/>", "instruction_cover: nowtime - last_instruction_time >1min 1/0 ", "light_state: 1/0 on/off ", "brightness: 1/0 high/low", 
"have_people: 0/1 no/have (updata the last_people)", "nobody_set: 0/1 /(have_people == 0 && nowtime - last_people > 2min 1)", 
"button_set: 1/0 push/no" ]
    '''
    
    
    parameters_list = [l_instruction,\
              l_currentuser,\
              l_authoritycompara,\
              l_instruction_cover,\
              l_light_state,\
              l_brightness,\
              l_have_people,\
              l_nobody_set,\
              l_button_set]

    
    
# =============================================================================
# 
#     #add the fuction of algorism 
#     (int)r_action, (str)r_message, (int)r_status = fuction(parameters_list) 
#     turn on(1) or off(0) ,  the information,  cmd can be done(1) or not(0)
#     
# =============================================================================
    ''' updata the whole values '''
    if int(r_status) == 1:              # when the cmd been done
        last_authority[rid] = l_currentuser
        last_instruction_time[rid] = l_nowtime
    if motion:
        last_people[rid] = l_nowtime
    return r_action, r_message, r_status








class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    def do_POST(self):
        """Serve a POST request."""
        print('we got it')
        req = {"state": 1, 'status':0,  'message': 'none'}
        remainbytes = int(self.headers['content-length'])
        #print(help(self.rfile))
        datas = self.rfile.read(int(self.headers['content-length']))
    #    line = self.rfile.readline()
        #print(remainbytes)
        #print(datas)
        
        #print(help(datas))
        a = datas.decode()
        r_action, r_message, r_status = do_json(a)
        
        req['state'] = r_action
        req['status'] = r_status
        req['message'] = r_message
        
        
        self.send_response(200)
        self.send_header("Content-type","json")
        self.end_headers()
        self.wfile.write(json.dumps(req).encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    #print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
