import threading
from tkinter import *
import requests
import base64
import numpy as np
import cv2
from PIL import Image, ImageTk
import Processing
import time
from queue import Queue

url = 'http://192.168.240.22:5000/'

class Automation:
    def __init__(self, stream_elem=None, overlay_elem=None):
        self.stream_elem = stream_elem
        self.overlay_elem = overlay_elem

        self.movement_queue = Queue()
        self.stop_event = threading.Event()
        self.line_type_detected = None

    def start_threads(self):
        video_thread = threading.Thread(target=self.update_vid_stream)
        video_thread.daemon = True
        video_thread.start()

        # movement_thread = threading.Thread(target=self.execute_movements)
        # movement_thread.daemon = True
        # movement_thread.start()
        
        # return video_thread, movement_thread
        return video_thread
    
    def update_vid_stream(self):
        while True:
            try:
                response = requests.get(url + 'vidstream')
                b64_image = response.json().get('frame')
                if not b64_image:
                    print('received empty frame from api')
                    continue

                decoded_img = base64.b64decode(b64_image)
                np_image = np.frombuffer(decoded_img, dtype=np.uint8)
                stream = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
                if stream is None:
                    print('failed to decode image')
                    continue

                overlay = Processing.apply_overlay(stream)

                stream = cv2.resize(stream, (400, 300))
                overlay = cv2.resize(overlay, (400, 300))

                stream = cv2.cvtColor(stream, cv2.COLOR_BGR2RGB)
                overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

                stream = ImageTk.PhotoImage(Image.fromarray(stream))
                overlay = ImageTk.PhotoImage(Image.fromarray(overlay))

                if self.stream_elem.winfo_exists() and self.overlay_elem.winfo_exists():
                    self.stream_elem.imgtk = stream
                    self.stream_elem.configure(image=stream)

                    self.overlay_elem.imgtk = overlay
                    self.overlay_elem.configure(image=overlay)
                else:
                    break
            except Exception as e:
                print(f'error in video stream: {e}')
                time.sleep(0.1)

    # old function for automation
    # def update_vid_stream(self):
    #     while True:
    #         try:
    #             response = requests.get(url + 'vidstream')
    #             b64_image = response.json().get('frame')
    #             if not b64_image:
    #                 print('received empty frame from api')
    #                 continue

    #             decoded_img = base64.b64decode(b64_image)
    #             np_image = np.frombuffer(decoded_img, dtype=np.uint8)
    #             stream = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    #             if stream is None:
    #                 print('failed to decode image')
    #                 continue

    #             overlay, line_type = Processing.apply_overlay(stream, self.movement_queue)

    #             if line_type != self.line_type_detected:
    #                 self.line_type_detected = line_type
    #                 print(f'line type: {line_type}')

    #             stream = cv2.resize(stream, (400, 300))
    #             overlay = cv2.resize(overlay, (400, 300))

    #             stream = cv2.cvtColor(stream, cv2.COLOR_BGR2RGB)
    #             overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

    #             stream = ImageTk.PhotoImage(Image.fromarray(stream))
    #             overlay = ImageTk.PhotoImage(Image.fromarray(overlay))

    #             if self.stream_elem.winfo_exists() and self.overlay_elem.winfo_exists():
    #                 self.stream_elem.imgtk = stream
    #                 self.stream_elem.configure(image=stream)

    #                 self.overlay_elem.imgtk = overlay
    #                 self.overlay_elem.configure(image=overlay)
    #             else:
    #                 break
    #         except Exception as e:
    #             print(f'error in video stream: {e}')
    #             time.sleep(0.1)

    def execute_movements(self):
        while not self.stop_event.is_set():
            try:
                try:
                    command, data = self.movement_queue.get(timeout=0.5)
                except Exception:
                    continue

                if command == 'horizontal_line_detected':
                    self.horizontal_line_sequence()
                elif command == 'move':
                    direction, duration = data
                    self.post_direction(direction)
                    time.sleep(duration)

                self.movement_queue.task_done()
            except Exception as e:
                print(f'error in movement automation: {e}')

    def horizontal_line_sequence(self):
        self.post_direction('stop')
        time.sleep(0.3)

        self.post_direction('forward')
        time.sleep(6.5)

        self.post_direction('stop')
        time.sleep(0.3)

        self.post_direction('left')
        time.sleep(1.05)

        self.post_direction('stop')
        time.sleep(0.3)

        self.post_direction('forward')
        time.sleep(5.0)

        self.post_direction('stop')
        time.sleep(60.0)

    def post_direction(self, direction):
        try:
            endpoint = url + 'moving'
            data = {'direction': direction}
            req = requests.post(endpoint, json=data)
        except Exception as e:
            print(f'error posting to api: {e}')

    def stop_threads(self):
        self.stop_event.set()
