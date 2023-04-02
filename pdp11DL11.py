"""PDP11 DL11 communications console"""

from tkinter import *
from tkinter import scrolledtext

window = Tk()
window.title("Welcome to LikeGeeks app")
window.geometry('350x200')
lbl = Label(window, text="Hello") # doesn't work. likegeeks lies
lbl = Label(window, text="Hello", font=("Arial Bold", 50)) # doesn't work. likegeeks lies
lbl.grid(column=0, row=0) # doesn't work. likegeeks lies
#txt = Entry(window,width=10)
#txt.grid(column=1, row=0)
def clicked():
    lbl.configure(text="Button was clicked !!")

btn = Button(window, text="Click Me", command=clicked)
    # Button causes background of windo to turn black
    # bg and fg don't work: , bg="orange", fg="red"
btn.grid(column=2, row=0)
txt = scrolledtext.ScrolledText(window,width=40,height=10) # that's fucking ugly
txt.grid(column=0, row=0)


window.mainloop()