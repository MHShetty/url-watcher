from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from threading import Timer
from datetime import datetime
from dateutil import tz
from tkinter.ttk import Progressbar

import webbrowser
import re
import winsound
import dateutil.parser
import os
import time
import threading
import math
import requests
import constants
import textwrap

class MainWindow(Tk):

  def __init__(self):
    super(). __init__() 

    self.timer = None
    self.FVD = (self.register(self.validate_float), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
    self.hLM = False

    self.title("URL Watcher")
    self.iconphoto(False, PhotoImage(file = constants.logo_path))

    self.geometry('420x367')
    self.grid_columnconfigure(1, weight=1)

    self.placeholder = Label(self, text="", anchor='w', font=("Arial", 2))
    self.placeholder.grid(row=0, column=0)    

    ## Designing the URL section

    self.urlLabel = Label(self, text="", anchor='w')
    self.urlLabel.grid(row=1, column=0, sticky=W, padx=8, pady=2)

    # The label of URL text box
    self.urlLabel = Label(self, text="URL:  ", anchor='w')
    self.urlLabel.grid(row=1, column=0, sticky=W, padx=8, pady=2)

    # The URL text box
    self.urlSV = StringVar()
    self.urlSV.trace("w", self.key_pressed)
    self.urlBox = Entry(self, textvariable=self.urlSV)
    self.urlBox.grid(row=1, column=1, sticky=W+E, padx=8, pady=2)

    # Designing the status code section
    self.scLabel = Label(self, text="Current Status Code:  ", anchor='w')
    self.scLabel.grid(row=2, column=0, sticky=W, padx=8, pady=2)
    self.scBox = Label(self, text="Waiting for URL...", anchor='w')
    self.scBox.grid(row=2, column=1, sticky=W, padx=8, pady=2)

    ## Designing the last modified section
    self.lmLabel = Label(self, text="Last Modified:  ", anchor='w')
    self.lmLabel.grid(row=3, column=0, sticky=W, padx=8, pady=2)
    self.lmBox = Label(self, text="-", anchor='w')
    self.lmBox.grid(row=3, column=1, sticky=W, padx=8, pady=2)

    ## Designing the Interval section
    self.inLabel = Label(self, text="Interval (in seconds):  ", anchor='w')
    self.inLabel.grid(row=4, column=0, sticky=W, padx=8, pady=2)
    self.inBox = Entry(self, validate = 'key', validatecommand = self.FVD)
    self.inBox.grid(row=4, column=1, sticky=W+E, padx=8, pady=2)

    ## Designing the Duration section
    self.durLabel = Label(self, text="Duration (in seconds):  ", anchor='w')
    self.durLabel.grid(row=5, column=0, sticky=W, padx=8, pady=2)
    self.durBox = Entry(self, validate = 'key', validatecommand = self.FVD)
    self.durBox.grid(row=5, column=1, sticky=W+E, padx=8, pady=2)

    ## Designing the Notify When? section

    # The label for Notify When? radio buttons
    self.nwLabel = Label(self, text="Notify which change?  ", anchor='w')
    self.nwLabel.grid(row=6, column=0, sticky=W, padx=8, pady=2)

    self.nwFrame = Frame(self)
    self.nwFrame.grid(row=6, column=1, sticky=W+E)
    self.nwFrame.grid_columnconfigure(1, weight=1)

    # The Notify When? radio buttons
    self.nwSV = BooleanVar(value=True)
    self.nwsc = Radiobutton(self.nwFrame, indicatoron=False, text="Status Code", variable=self.nwSV, value=True)
    self.nwsc.grid(row=0, column=0, sticky=W+E, padx=1, pady=3)
    self.nwlm = Radiobutton(self.nwFrame, indicatoron=False, text="Last Modified", variable=self.nwSV, value=False, state=DISABLED)
    self.nwlm.grid(row=0, column=1, sticky=W+E, padx=1, pady=3)
    self.nwbt = Radiobutton(self.nwFrame, text="Either", variable=self.nwSV, indicatoron=False, value=None, state=DISABLED)
    self.nwbt.grid(row=0, column=2, sticky=W+E, padx=1, pady=3)

    ## Designing the Status Code Section

    # Creating the required components
    self.eStatusLabel = Label(self, text="Expected Status Code:", anchor='w')
    self.eStatusLabel.grid(row=7, column=0, sticky=W, padx=8, pady=2)

    self.eStatusVar = StringVar(self, "Choose an option")
    self.eStatusBox = Menubutton(self, textvariable=self.eStatusVar, indicatoron=True)
    self.topMenu = Menu(self.eStatusBox, tearoff=False)
    self.eStatusBox.grid(row=7, column=1, sticky=W+E, padx=8, pady=2)
    self.eStatusBox.configure(menu=self.topMenu)

    self.eStatusBox.config(state = DISABLED)

    # Generating the options using
    if isinstance(constants.http_status_details, dict):
      for key, values in constants.http_status_details.items():
        menu = Menu(self.topMenu, tearoff=False)
        self.topMenu.add_cascade(label=key, menu=menu)
        values = {key[:3]:"All", **values}
        for code, desc in values.items():
          menu.add_radiobutton(label=f"{code}: {desc}", variable=self.eStatusVar, value=f"{code}: {desc}")

    # Designing the action 
    self.aPLabel = Label(self, text="Action to be performed", anchor='w')
    self.aPLabel.grid(row=8, column=0, sticky=W, padx=8, pady=2)
    self.aPVar = StringVar(self, "Play Buzzer")
    self.aPBox = OptionMenu(self, self.aPVar, "Exit on done", "Play Buzzer", "Leave Idle", "Open in browser", "Execute script")
    
    self.aPBox.grid(row=8, column=1, sticky=W+E, padx=8, pady=2)
    self.scriptPath = None
    def callback(*args):
      if self.aPVar.get()=="Execute script":
        filename = askopenfilename(filetypes=[("Python Script (*.py)", ".py")])
        if filename:
          self.scriptPath = filename
          filename = os.path.basename(filename)
          self.after(0, lambda: self.aPVar.set(f"Execute script: {filename}"))
        else:
          self.after(0, lambda: self.aPVar.set("Play Buzzer"))
          self.scriptPath = None
      elif self.aPVar.get() and not self.aPVar.get().startswith("Execute script"):
        self.scriptPath = None

    self.aPVar.trace("w", callback)

    # Designing the Watcher Label section
    self.wlLabel = Label(self, text="Watcher Label", anchor='w')
    self.wlLabel.grid(row=9, column=0, sticky=W, padx=8, pady=2)
    self.wlBox = Entry(self)
    self.wlBox.grid(row=9, column=1, sticky=W+E, padx=8, pady=2)

    # The function to be called on submit
    def onSubmit():

      url = None
      csc = None

      wl = self.wlBox.get()

      ## Check if the given link has a valid status code and perform the necessary actions accordingly

      try:
        # Test the status code
        csc = int(self.scBox.cget("text"))     
        # If it's valid then store the url and proceed
        url = self.getUrl()
      except ValueError:
        messagebox.showwarning("Invalid URL", "Please enter a valid URL or wait for the status code to load before proceeding.")
        return

      # Converting the interval that is guaranteed to be float to float
      interval = self.inBox.get()
      if len(interval)==0: interval=0
      else: interval = float(interval)

      # Converting the duration that is guaranteed to be float to float
      duration = self.durBox.get()
      if len(duration)==0: duration=math.inf
      else: duration = float(duration)

      # Retrieve which change needs to be notified
      # True - Status Code
      # False - Last Modified
      # None - Either
      nwc = None
      try:
        nwc = self.nwSV.get()
      except:
        nwc = None

      lmd = None
      esc = None
 
      if not nwc:
        lmd = self.lmBox.cget("text")

      if nwc!=False:
        esc = self.eStatusVar.get()
        if esc=="Choose an option":
          messagebox.showwarning("Invalid Status Code", "Please choose an status code from the given dropdown.")
          return

      atb = self.aPVar.get()

      params = {"url": url, "csc": csc, "interval": interval, "duration": duration, "nwc": nwc, "atb": atb, 'wl':wl}
      if lmd: params["lm"] = lmd
      if esc:
        print(esc, csc)
        if re.search(esc[0:3].replace('xx','..'), str(csc)):
          if messagebox.askquestion("Condition already satisfied", "The current status code and expected status code already match. Do you still like to proceed to proceed?") == 'no':
            return          
        params["esc"] = esc

      if atb.startswith("Execute script"):
        params["script-path"] = self.scriptPath

      # Create a URL watcher
      URLWatcher(params) 

    self.sButton = Button(self, text="Start Watching...", command=onSubmit)
    self.sButton.grid(row=10, columnspan=2, sticky=W+E, padx=8, pady=12)

    self.helpDesc = """Help:

1. The URL textbox specified the URL to be watched. (Valid URLs always have some status code)

2. Interval specifies the time between two successive requests.

3. Duration specifies the total time for which the watcher should watch. If set to 0, makes the watcher run until the condition is satisfied.

4. If the last modified is '-', that means that either the URL is invalid or the server doesn't support that feature. In such cases, the app will disable the `Last Modified` and `Either` option.

5. The expected status code option will work when there is a valid URL and `Last Modified` is not selected.
    """

    self.hButton = Button(self, text="Help Menu", command=lambda: messagebox.showinfo("Help Menu", self.helpDesc))
    self.hButton.grid(row=11, columnspan=2, sticky=W+E, padx=8, pady=2)

    self.cBox = Label(self, text="© Made in TPoly (2020-21)")
    self.cBox.grid(row=12, column=0, columnspan=2, sticky=N+S+W+E, padx=8, pady=6)

    self.resizable(False, False)

    try:
      self.mainloop()
    except:
      pass


  def key_pressed(self, index, mode, sv):    
    if self.timer and self.timer.is_alive():
      self.timer.cancel()

    self.timer = Timer(constants.debounce_duration, self.update_status)
    self.timer.start()


  def validate_float(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        elif len(value_if_allowed)==0:
            return True
        else: return False

  def getUrl(self):
    return self.urlBox.get()

  def getInterval(self):
    return self.inBox.get()

  def update_status(self, retry=False, redirect=False):
    self.eStatusBox.config(state = DISABLED)
    self.nwlm.config(state = DISABLED)
    self.nwbt.config(state = DISABLED)
    self.nwSV.set(True)
    if not redirect and not self.getUrl():
      self.scBox.config(text="Waiting for URL...")
      self.lmBox.config(text="-")
    else:
      r = None
      try:
        self.scBox.config(text="Loading...")
        self.lmBox.config(text="...")
        r = requests.head(self.getUrl())

        if r.status_code==302 and r.headers['Location']:
          self.urlBox.config(text=r.headers['Location'])
          self.scBox.config(text="Redirecting...")
          self.update_status(redirect=True)

        self.scBox.config(text=str(r.status_code))
        self.eStatusBox.config(state = NORMAL)
        if 'last-modified' in r.headers:
          date = dateutil.parser.parse(r.headers['last-modified']).astimezone(to_zone)
          self.lmBox.config(text=date.strftime("%a, %e %B %Y %H:%M:%S IST"))
          self.nwlm.config(state = NORMAL)
          self.nwbt.config(state = NORMAL)
        else:
          self.lmBox.config(text="Not specified for this URL by the server.")
      except requests.exceptions.MissingSchema:
        self.scBox.config(text="Please specify the schema (http/https) in the url.")
      except requests.exceptions.InvalidSchema:
        self.scBox.config(text="The schema (http/https) is invalid.")
      except requests.exceptions.InvalidURL:
        self.scBox.config(text="The syntax of the URL is invalid.")
      except requests.exceptions.ConnectionError:
        if retry: self.scBox.config(text="The above URL seems to be invalid (Not found)")
        else: self.update_status(True)      
      except BaseException as e:
        print(str(type(e))+" : "+str(e))
        self.scBox.config(text=str(type(e))+" : "+str(e))
      finally:
        if self.lmBox.cget("text")=="...": self.lmBox.config(text="-")

class URLWatcher:

  # Define your Progress Bar function, 
  def task(self):
    self.root.geometry('436x55')
    self.root.grid_columnconfigure(1, weight=1)

    ft = Frame(self.root)
    ft.grid(sticky=W+E, padx=8, pady=2)

    self.pb = Progressbar(ft, orient='horizontal', mode='indeterminate', length=420)
    self.pb.grid(row=0, column=0, sticky=W+E)
    self.pb.start(50)

    self.m = Message(self.root, text="We'll perform the desired action as soon as the given condition gets satisfied.", width=420, justify=CENTER)
    self.m.grid(row=1, column=0, sticky=W+E)

    self.root.mainloop() 

  def main_process(self):

    nwc = self.kwargs["nwc"]
    esc = self.kwargs["esc"]
    esc = esc[:3].replace('xx','..')
    url = self.kwargs['url']

    self.isNotDestroyed = True
    self.root.protocol("WM_DELETE_WINDOW", self.onTimeout)

    if self.kwargs["duration"] and self.kwargs["duration"]!=math.inf: self.root.after(int(self.kwargs["duration"]*1000), self.onTimeout)
    self.startTime = time.time()
    while self.isNotDestroyed:
      res = None
      try:
        res = requests.head(url)        
      except requests.exceptions.ConnectionError:
        print("Either the server is longer registered with the DNS or your internet connection is lost.")
        continue
      except BaseException as e:
        print(str(type(e))+" : "+str(e))
        self.onTimeout()

      if nwc==True:
        if re.search(esc, str(int(res.status_code))):
          self.perform_action()
          break
      elif nwc==False:
        date = dateutil.parser.parse(res.headers['last-modified']).astimezone(to_zone)
        if res.headers['last-modified']==date.strftime("%a, %e %B %Y %H:%M:%S IST"):
          self.perform_action()
          break
      else:
        date = dateutil.parser.parse(res.headers['last-modified']).astimezone(to_zone)
        if re.search(esc, str(res.status_code)) or re.search(esc, str(int(res.status_code))):
          self.perform_action()
          break
      time.sleep(self.kwargs['interval'])
    self.root.after_cancel(self.onTimeout)

  def onTimeout(self):
    self.isNotDestroyed = False
    self.root.destroy()

  def perform_action(self):
    self.m.configure(text="The expected change has been detected. You can now close this window.") 
    atb = self.kwargs["atb"]   
    if atb=='Play Buzzer':
      while self.isNotDestroyed:
        beep()
    elif atb=='Exit on done':
      print('Exit on done')
      self.onTimeout()
    elif atb=='Leave Idle':
      pass
    elif atb=='Open in browser':
      webbrowser.open(self.kwargs["url"])
    else:
      script_path = self.kwargs["script-path"]
      os.system(f"python \"{script_path}\"")
      

  def __init__(self, kwargs):
    self.kwargs = kwargs
    self.root = Tk()
    self.root.title(kwargs["wl"])
    self.t1=threading.Thread(target=self.main_process)
    self.t1.start()
    self.task()  # This will block while the mainloop runs
    self.t1.join()

def beep():
  for i in range(0, 3):
    winsound.Beep(2000, 100)
  for i in range(0, 3):
    winsound.Beep(2000, 400)
  for i in range(0, 2):
    winsound.Beep(2000, 50)
  time.sleep(0.7)

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

MainWindow()