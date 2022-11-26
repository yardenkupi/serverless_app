from multiprocessing import Process
import multiprocessing
import datetime
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse , parse_qs
from collections import deque
import os

SEC_TO_SLEEP = 3
TIME_BEFORE_TERMINATE = 6
hostName = "localhost"
serverPort = 8080

def sleep_and_sum(first, sec, return_dict):
    return_dict[multiprocessing.current_process().pid] = first + sec

class ServerAPP(BaseHTTPRequestHandler):
    def get_sleep_and_sum(self, url_parsed):
        print(f'parent pid:{os.getpid()}')
        query = url_parsed.query
        args = parse_qs(query)
        # Check for correct input
        if (("first" in args) and ("sec" in args) and (len(args) == 2)):
            first = int(args["first"][0])
            sec = int(args["sec"][0])
            p = Process(target=sleep_and_sum, args=(first, sec, return_dict))
            p.last_use = datetime.datetime.now()
            p.start()
            sleep(SEC_TO_SLEEP)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(return_dict[p.pid]).encode("utf-8"))


        else:
            # Case of wrong input
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str("Wrong input, please send first and sec numbers").encode("utf-8"))

    def do_GET(self):
        url_parsed = urlparse(self.path)
        if (url_parsed.path == '/sleep_and_sum'):
            self.get_sleep_and_sum(url_parsed)

        # else:
            #TODO 404  for wrong path

class MYThreadingHTTPServer(ThreadingHTTPServer):
    def service_actions(self):
        a = 1


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    webServer = MYThreadingHTTPServer((hostName, serverPort), ServerAPP)
    webServer.queue = deque()
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
