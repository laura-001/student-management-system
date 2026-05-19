#creating GUI
from tkinter import *
from PIL import ImageTk

window=Tk()

window.geometry("1280x700+0+0")#size of window
window.resizable(False,False)#prevents resizing of window

#backgroundImage = ImageTk.PhotoImage(file="bg.jpeg")#background image
#bglabel=Label(window,image=backgroundImage)
#bglabel.place(x=0,y=0)#places background image

loginFrame=Frame(window)
loginFrame.place(x=400,y=150)#places login frame

logoImage=PhotoImage(file="logo.png")#logo image
logoLabel=Label(loginFrame,image=logoImage)
logoLabel.grid(row=0,column=0)#places logo image

usernameImage=PhotoImage(file="user.png")#user image
usernameLabel=Label(loginFrame,image=usernameImage,text="Username",compound=LEFT,font=("times new roman",15,"bold"))#creates username label with image
usernameLabel.grid(row=1,column=0,pady=10)#places username label

usernameEntry=Entry(loginFrame)

window.mainloop()#keeps window open 