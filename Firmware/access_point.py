# main.py -- put your code here!
try:
    import usocket as socket
except:
    import socket

from config_storage import save_string, ssid_txt, pass_txt, fb_txt
from index import web_page
from machine import reset

text_ssid = None
text_pass = None

def extract_query(request_bytes):
    try:
        # Decode bytes to string
        request = request_bytes.decode()
        # First line of HTTP request
        first_line = request.split('\r\n')[0]
        # Example: "GET /?firstname=Rene&lastname=Lozano HTTP/1.1"
        path = first_line.split(' ')[1]  # "/?firstname=Rene&lastname=Lozano"

        result = {}
        if '?' in path:
            query = path.split('?', 1)[1]
            # return query
        else: 
            return None
        
        # Split by '&' to get key=value pairs
        for pair in query.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                import ubinascii
                i = 0
                decoded = b''
                while i < len(value):
                    if value[i] == '%' and i+2 < len(value):
                        hexval = value[i+1:i+3]
                        decoded += ubinascii.unhexlify(hexval)
                        i += 3
                    else:
                        decoded += value[i].encode()
                        i += 1
                result[key] = decoded.decode()
        return result
    except Exception as e:
        print("Error extracting query:", e)
        return ""

def run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        # print('Content = %s' % str(request))
        # raw_query = str(request)
        text_query = extract_query(request)
        if text_query:
            print(text_query)
            text_ssid = text_query.get("ssid")
            text_pass = text_query.get("pass")
            if text_ssid == '':
                text_ssid = "placeholder1"
            if text_pass == '':
                text_pass = "placeholder2"
            print("SSID: ", text_ssid)
            print("Password: ", text_pass)
            save_string(ssid_txt, text_ssid)
            save_string(pass_txt, text_pass)
            save_string(fb_txt, "continue")
            reset()
        response = web_page()
        conn.send(response)
        conn.close()