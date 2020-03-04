# Implementation based on:
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import socketserver

from threading import Condition
from http import server

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
            while True:
                with self.server.output.condition:
                    self.server.output.condition.wait()
                    frame = self.server.output.frame
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except:
            pass

    def log_message(self, format, *args):
        pass

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

streaming_output : StreamingOutput
streaming_server : StreamingServer

def camera_run():
    with picamera.PiCamera(resolution='640x480', framerate=10) as camera:
        global streaming_output
        streaming_output = StreamingOutput()

        camera.start_recording(streaming_output, format='mjpeg')

        try:
            address = ('', 8000)

            global streaming_server
            streaming_server = StreamingServer(address, StreamingHandler)
            streaming_server.output = streaming_output
            streaming_server.serve_forever()
        finally:
            camera.stop_recording()

def camera_stop():
    streaming_server.shutdown()
