from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import json

data = {'result': 'this is a frist test'}
host = ('localhost', 8888)

a = 'a'

def do_json(data):
    b = parse.parse_qs(data)
    print(b)
    print(type(b))
    datas = b
    print(datas['cmd_data'])
    authority = datas['authority']
    cmd_type = 0
    d_light = 0
    s_light = 0
    s_motion = 0
    s_button = 0
    n_time = datas['cmd_data']
    c = datas['sensors'][0]
    c = c.split("{")
    print("last sensors--- light:", s_light, "motion:", s_motion, "button:", s_button)
    for i in c:
        if len(i) > 10:
            d = i.split(',')
            if (d[1] == " 'type': 'light'") and \
            (d[2] == " 'data': 'bright'"):
                s_light = 1
            if (d[1] == " 'type': 'motion'") and \
            (d[2] == " 'data': 'Exist'"):
                s_motion = 1
            if (d[1] == " 'type': 'button'") and \
            (d[2] == " 'data': 'Pressed'"):
                s_button = 1
    print("now sensors--- light:", s_light, "motion:", s_motion, "button:", s_button)
    r_action = 1
    r_message = 'none'
# =============================================================================
# 
#     #加入计算控制函数
#     r_action, r_message = fuction(Room_id = datas['Room_id']#\
#     f_authority = datas['authority'],\
#     f_cmd_type = cmd_type,\
#     f_d_light = d_light,\
#     f_s_light = s_light,\
#     f_s_motion = s_motion,\
#     f_s_button = s_button,\
#     f_n_time = datas['cmd_data']) 
#     
# =============================================================================
    return r_action, r_message








class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    def do_POST(self):
        """Serve a POST request."""
        print('we got it')
        req = {"state": 1, 'message': 'none'}
        remainbytes = int(self.headers['content-length'])
        #print(help(self.rfile))
        datas = self.rfile.read(int(self.headers['content-length']))
    #    line = self.rfile.readline()
        #print(remainbytes)
        #print(datas)
        
        #print(help(datas))
        a = datas.decode()
        r_action, r_message = do_json(a)
        
        req['state'] = r_action
        req['message'] = r_message
        
        
        self.send_response(200)
        self.send_header("Content-type","json")
        self.end_headers()
        self.wfile.write(json.dumps(req).encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    #print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()