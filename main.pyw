from tkinter import * 
from PIL import Image, ImageTk

class Animation(Label):
    def __init__(self, master):
        self.limg = ImageTk.PhotoImage(Image.open("startup-animation-last.png"))
        im = Image.open('startup-animation.gif')
        seq =  []
        # Reading all the frames of the gif in list seq
        try:
            while 1:
                seq.append(im.copy())
                im.seek(len(seq))# skip to next frame
        except EOFError:
            pass
        try:
            self.delay = im.info['duration']
        except KeyError:
            self.delay = 100

        first = seq[0].convert('RGBA')
        self.frames = [ImageTk.PhotoImage(first)]

        Label.__init__(self, master, image=self.frames[0])
        self.config(borderwidth=0, highlightthickness=0)

        temp = seq[0]
        for image in seq[1::]:
            temp.paste(image)
            frame = temp.convert('RGBA')
            self.frames.append(ImageTk.PhotoImage(frame))

        self.idx = 0

        self.cancel = self.after(self.delay, self.play)

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx += 1
        if self.idx == len(self.frames):
          self.config(image=self.limg)
          self.image=self.limg
        else:
          self.cancel = self.after(self.delay, self.play)        

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

root=Tk()
root.overrideredirect(True) # turns off title bar, geometry

# make a frame for the title bar
title_bar = Frame(root, bg='#181818', bd=2, highlightthickness=0)

title = Entry(title_bar, text='URL Watcher', bg="#181818", bd=0, font="bold", fg='white', highlightthickness=0)

# put a close button on the title bar
close_button = Button(title_bar, text=' X ', command=root.destroy, bg="#181818", padx=2, pady=2, activebackground='red', bd=0, font="bold", fg='white', highlightthickness=0)

# a canvas for the main area of the window
window = Canvas(root, bg='#181818', highlightthickness=0)

# pack the widgets
title_bar.pack(expand=1, fill=X)
close_button.pack(side=RIGHT)
window.pack(expand=1, fill=BOTH)
xwin=None
ywin=None
# bind title bar motion to the move window function

def move_window(event):
    root.geometry('+{0}+{1}'.format(event.x_root, event.y_root))

def change_on_hovering(event):
    global close_button
    close_button['bg']='red'

def return_to_normalstate(event):
    global close_button
    close_button['bg']='#181818'

close_button.bind('<Enter>', change_on_hovering)
close_button.bind('<Leave>', return_to_normalstate)
# title_bar.bind('<B1-Motion>', move_window)

def animComplete():
  root.destroy()
  import mipro

anim = Animation(window)
anim.pack()
center(root)
root.after(8000, animComplete)
root.mainloop()
