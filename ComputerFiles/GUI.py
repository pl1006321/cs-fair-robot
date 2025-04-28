from tkinter import *
from tkinter.scrolledtext import *
from tkinter.font import Font
from PIL import Image, ImageTk
import os
import subprocess
import socket
from threading import Thread
import cv2
import numpy as np
import Database
import requests
from tkinter import messagebox
import base64
from datetime import datetime
import Automation

url = 'http://192.168.240.22:5000/'

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title('user login')
        self.root.geometry('450x300')
        self.database = Database.Database()

        self.video_running = False
        self.video_paused = False
        self.cap = None

        self.setup_login_page()

    def setup_login_page(self):
        self.user_entry_text = StringVar()
        self.pw_entry_text = StringVar()

        entries_panel = Frame(self.root, bg="#927a7d")
        entries_panel.place(x=225, y=60)

        welcome_to_label = Label(text='Welcome to', fg="#FFFFFF", bg="#927a7d", font=('Poppins', 25))
        welcome_to_label.place(x=15, y=15)

        robogo_label = Label(text='robogo!', fg="#FFFFFF", bg="#927a7d", font=('Poppins', 35, "bold"))
        robogo_label.place(x=15, y=45)

        kawaii = Image.open("ComputerFiles/images/kawaii.png")
        kawaii = kawaii.resize((190, 120))
        self.kawaii = ImageTk.PhotoImage(kawaii)

        kawaii_label = Label(image=self.kawaii, borderwidth=0, highlightthickness=0)
        kawaii_label.place(x=15, y=90)

        username_entry_label = Label(entries_panel, text='username: ', fg="#FFFFFF", bg="#927a7d", font='50')
        username_entry_label.grid(row=2, column=1, padx=5, pady=5, sticky='W')

        username_entry = Entry(entries_panel, textvariable=self.user_entry_text)
        username_entry.grid(row=3, column=1, padx=5, pady=5)

        password_entry_label = Label(entries_panel, text='password: ', fg="#FFFFFF", bg="#927a7d")
        password_entry_label.grid(row=4, column=1, padx=5, pady=5, sticky='W')

        password_entry = Entry(entries_panel, textvariable=self.pw_entry_text, show='*')
        password_entry.grid(row=5, column=1, padx=5, pady=5)

        buttons_panel = Frame(self.root, bg="#927a7d")
        buttons_panel.place(x=215, y=220)

        login_button = Button(buttons_panel, text='login', command=self.login)
        login_button.grid(row=1, column=1, ipadx=3, ipady=2, padx=5, pady=5, )

        create_acc_button = Button(buttons_panel, text='create account', command=self.create_acc)
        create_acc_button.grid(row=1, column=2, ipadx=3, ipady=2, padx=5, pady=5)

    def login(self):
        username = self.user_entry_text.get()
        password = self.pw_entry_text.get()

        if not username or not password:
            messagebox.showinfo(message='one or more entries were left blank. please try again')
            return
        
        if not self.database.user_exists(username):
            messagebox.showinfo(message='invalid username. please try again')
            return
    
        if password != self.database.get_password(username):
            messagebox.showinfo(message='invalid password. please try again')
            return

        self.username = username
        
        messagebox.showinfo(message=f'login successful! welcome {username}')
        self.create_robot_gui()

    def create_acc(self):
        username = self.user_entry_text.get()
        password = self.pw_entry_text.get()

        if not username or not password:
            messagebox.showinfo(message='one or more entries were left blank. please try again')
            return
        
        if self.database.user_exists(username):
            messagebox.showinfo(message='account with this username already exists.')
            return
        
        self.database.insert_user(username, password)
        messagebox.showinfo(message=f'account creation successful!')

    def post_direction(self, direction):
        try:
            endpoint = url + 'moving'
            data = {'direction': direction}
            req = requests.post(endpoint, json=data)
            print('command sent successfully')
            self.logging(direction)
        except:
            print('something happened; error')

    def play_button(self):
        self.automation = Automation.Automation(self.stream_elem, self.overlay_elem)
        # self.video_thread, self.movement_thread = self.automation.start_threads()
        self.video_thread = self.automation.start_threads()

    def create_robot_gui(self):
        robot_gui = Toplevel(bg='#927a7d')
        robot_gui.title('robot gui')
        robot_gui.geometry('1020x700')

        custom_font = Font(family='Poppins', size=20)
        
        vid_stream_panel = Frame(robot_gui, bg="#927a7d")
        vid_stream_panel.grid(row=5, column=1, rowspan=1, padx=5, pady=5, sticky='NWSE')

        buttons_panel = Frame(robot_gui, bg="#927a7d")
        buttons_panel.place(x=620, y=50)

        vid_overlay_panel = Frame(robot_gui, bg="#927a7d")
        vid_overlay_panel.grid(row=6, column=1, rowspan=1, padx=5, pady=5, sticky='NWSE')

        log_panel = Frame(robot_gui, bg="#927a7d")
        log_panel.place(x=550, y=450)

        self.text_area = ScrolledText(log_panel, width=45, height=5)
        self.text_area.grid(row=1, padx=40, pady=5, ipadx=20, ipady=20, sticky='e')
        self.text_area.config(state='disabled')

        log_button = Button(log_panel, text='open log file', command=self.open_log_file, font=custom_font, padx=5, pady=7)
        log_button.grid(row=2, padx=4, pady=5, ipadx=5, ipady=5)

        black_img = np.zeros((270, 480, 3), dtype=np.uint8)
        black_img = ImageTk.PhotoImage(Image.fromarray(black_img))

        self.stream_elem = Label(vid_stream_panel, image=black_img, bg='black')
        self.stream_elem.image = black_img
        self.stream_elem.grid(padx=50, pady=40)

        self.overlay_elem = Label(vid_overlay_panel, image=black_img, bg='black')
        self.overlay_elem.image = black_img
        self.overlay_elem.grid(padx=50, pady=10)

        # video_thread = Thread(target=update_vid_stream, args=(stream_elem,overlay_elem))
        # video_thread.daemon = True 
        # video_thread.start()

        up_arrow = Image.open('ComputerFiles/images/arrow.png').resize((50, 50))
        self.up_arrow = ImageTk.PhotoImage(up_arrow)

        forward = Button(buttons_panel, image=self.up_arrow, font=custom_font,)
        forward.grid(row=1, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')
        forward.bind('<ButtonPress-1>', lambda event: self.post_direction('forward'))
        forward.bind('<ButtonRelease-1>', lambda event: self.post_direction('stop'))

        left_arrow = up_arrow.rotate(90)
        self.left_arrow = ImageTk.PhotoImage(left_arrow)

        left = Button(buttons_panel, image=self.left_arrow, font=custom_font, padx=5, pady=7)
        left.grid(row=2, column=1, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')
        left.bind('<ButtonPress-1>', lambda event: self.post_direction('left'))
        left.bind('<ButtonRelease-1>', lambda event: self.post_direction('stop'))

        play_img = Image.open('ComputerFiles/images/play.png').resize((70, 50))
        self.play_img = ImageTk.PhotoImage(play_img)

        play = Button(buttons_panel, image=self.play_img, font=custom_font, padx=5, pady=7, command = self.play_button)
        play.grid(row=2, column=4, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

        stop_img = Image.open('ComputerFiles/images/stop_btn.png').resize((50, 50))
        self.stop_img = ImageTk.PhotoImage(stop_img)

        stop = Button(buttons_panel, image=self.stop_img, font=custom_font, padx=5, pady=7, command = lambda: self.post_direction('stop'))
        stop.grid(row=2, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

        right_arrow = up_arrow.rotate(-90)
        self.right_arrow = ImageTk.PhotoImage(right_arrow)

        right = Button(buttons_panel, image=self.right_arrow, font=custom_font, padx=5, pady=7)
        right.grid(row=2, column=3, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')
        right.bind('<ButtonPress-1>', lambda event: self.post_direction('right'))
        right.bind('<ButtonRelease-1>', lambda event: self.post_direction('stop'))

        back_arrow = up_arrow.rotate(180)
        self.back_arrow = ImageTk.PhotoImage(back_arrow)

        backward = Button(buttons_panel, image=self.back_arrow, font=custom_font, padx=5, pady=7)
        backward.grid(row=3, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we',)
        backward.bind('<ButtonPress-1>', lambda event: self.post_direction('backward'))
        backward.bind('<ButtonRelease-1>', lambda event: self.post_direction('stop'))

        ip_addr = socket.gethostbyname(socket.gethostname())
        time = datetime.now() 
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')        
        msg = f'{self.username}@{ip_addr} has logged in at {timestamp}\n'
        with open('system_log.txt', 'a') as file:
            file.write(msg)
        file.close()
        self.text_area.config(state='normal')
        self.text_area.insert(END, msg)
        self.text_area.see(END)
        self.text_area.config(state='disabled')

    # def update_vid_stream(element1, element2): 
    #     global url
    #     while True:
    #         b64_image = requests.get(url + 'vidstream').json()['frame'] # extract video stream from api
    #         decoded_img = base64.b64decode(b64_image) # decode the b64 string that is returned
    
    #         np_image = np.frombuffer(decoded_img, dtype=np.uint8) # convert string to numpy array
    #         stream = cv2.imdecode(np_image, cv2.IMREAD_COLOR) # convert numpy array to image
    
    #         overlay = apply_overlay(stream) # apply the overlay onto the frame 
    
    #         stream = cv2.resize(stream, (400, 300))
    #         overlay = cv2.resize(overlay, (400, 300))
    
    #         # cv2 uses bgr, tkinter uses rgb 
    #         stream = cv2.cvtColor(stream, cv2.COLOR_BGR2RGB)
    #         overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
    
    #         # create an imagetk of both images 
    #         stream = ImageTk.PhotoImage(Image.fromarray(stream))
    #         overlay = ImageTk.PhotoImage(Image.fromarray(overlay))
    
    #         # checks to see if both elements still exist, in case the gui is closed 
    #         if element1.winfo_exists() and element2.winfo_exists():
    #             # sets respective elements to the image frames 
    #             element1.imgtk = stream
    #             element2.imgtk = overlay
    #             element1.configure(image=stream)
    #             element2.configure(image=overlay) 
    #         else:
    #             break

    def logging(self, direction):
        try:
            endpoint = url + 'logging'
            log = requests.get(endpoint)
            log = log.json()
            log_str = f"{log['Timestamp']} - {self.username}@{log['IP Address']} sent the command: {direction}\n"
            with open("system_log.txt", 'a') as file:
                file.write(log_str)
            self.text_area.config(state='normal')
            self.text_area.insert(END, log_str)
            self.text_area.see(END)
            self.text_area.config(state='disabled')
        except:
            print('an error occured sorry!')

    def stop_video(self):
        self.video_paused = True

    def open_log_file(self):
        file_path = 'system_log.txt'
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        subprocess.call(('open', file_path))

    @staticmethod
    def launch_guis():
        root = Tk()
        root.configure(bg='purple')
        root['bg'] = '#927a7d' 
        app = GUI(root)
        root.mainloop()
