from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import json
import network

data = {'result of http': 'this is a frist test'}
host = ('49.140.60.138', 8888)

last_authority = {}
last_instruction_time = {}
last_people = {}
last_timeout = {}


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
    l_timeout = 60
    b = parse.parse_qs(data)
    print(b)
    print(type(b))
    data = b


    
    ''' load the room id  '''
    l_rid = json.loads(data['room'][0].replace("'", '"'))
    l_bid = json.loads(data['building'][0].replace("'", '"'))
    rid = str(l_bid) + "-" + str(l_rid)
    l_time = float(data['time'][0])
    l_timeout = json.loads(data['timeout'][0].replace("'", '"'))




    ''' sensors '''
    s = json.loads(data['sensors'][0].replace("'", '"'))          
    brightness = 0
    motion = 0
    button = 0
    for i in s:
        if i['data'] == 'offline':
            break
        if i['type'] == 3:
            brightness = brightness | int(i['value']) 
        if i['type'] == 4:
            motion = motion | int(i['value'])
        if i['type'] == 5:
            button = button | int(i['data'])
    '''devices'''
    d = json.loads(data['devices'][0].replace("'", '"'))
    light = 0
    for i in d:
        if i['value'] == 'offline':
            break
        if i['type'] == 1:
            light = light | int(i['value'])


    ''' set the parameter '''

    l_currentuser = data['priority'][0]      #0 no cmd  1 student 2teacher
    l_instruction = data['command'][0]

    # check the authority
    if rid not in last_authority.keys():
        last_authority[rid] = 1
    if l_currentuser > last_authority[rid]:
        l_authoritycompara = '1'
    # check the time
    
    
    l_nowtime = float(data['time'][0])
    l_timeout = float(data['timeout'][0])
    if rid not in last_timeout.keys():      # set last time out
        last_timeout[rid] = 60
    
    
    if rid not in last_instruction_time.keys():
        last_instruction_time[rid] = 0.0
    if l_nowtime - last_instruction_time > last_timeout[rid]:
        l_instruction_cover = 1
        
    last_timeout[rid] = l_timeout
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
    
    ''' for lights  '''
    d = json.loads(data['devices'][0].replace("'", '"'))
    nl = 0 # the number of light
    for i in d:
        if i['type'] == 1:
            list1 = [WME('Instruction', l_instruction, nl),
             WME('Current_User', l_currentuser, nl),
             WME('Authority_Compare', l_authoritycompara, nl),
             WME('Instruction_Cover', l_instruction_cover, nl),
             WME('Light_State', str(data[value]), nl),
             WME('Brightness', l_brightness, nl),
             WME('Have_People', l_have_people, nl),
             WME('Nobody_Set', l_nobody_set, nl),
             WME('Button_Pressed', l_button_set, nl)]
            print(list1)
            net.run(list1, nl)
            r_action, r_message = net.dooutput()
    
    
    r_action = 0
    r_status = 0
    r_message = 'none'
    
# =============================================================================
# 
#     #加入计算控制函数
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
        print('we got it :')
        req = {"state": 1, 'status':0,  'message': 'none'}
        remainbytes = int(self.headers['content-length'])
        #print(help(self.rfile))
        datas = self.rfile.read(int(self.headers['content-length']))
    #    line = self.rfile.readline()
        #print(remainbytes)
        #print(datas)
        
        #print(help(datas))
        a = datas.decode()
        print(a)
        b = parse.parse_qs(a)
        print('it is : ')
        print(b)
        
        
        r_action = 0
        r_status = 0
        r_message = 0
        
        #r_action, r_message, r_status = do_json(a)
        
        req['state'] = r_action
        req['status'] = r_status
        req['message'] = r_message
        
        
        self.send_response(200)
        self.send_header("Content-type","json")
        self.end_headers()
        self.wfile.write(json.dumps(req).encode())

if __name__ == '__main__':
    net = init_network()
    server = HTTPServer(host, Resquest)
    #print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()