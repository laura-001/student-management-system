#creating GUI
from pathlib import Path
from tkinter import *
from PIL import ImageTk
from tkinter import messagebox

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR.parent / "assets" / "images"

def login():
    if usernameEntry.get()=="" or passwordEntry.get()=="":#checks if username and password are null
        messagebox.showerror("Error","All fields are required")#shows error message

    elif usernameEntry.get()=="Laura" and passwordEntry.get()=="1234":
        messagebox.showinfo("Success","Login successful")#shows success message
        
    elif usernameEntry.get()=="Admin" and passwordEntry.get()=="admin":
        messagebox.showinfo("Success","Login successful")#shows success message    
    else:
        messagebox.showerror("Error","Invalid username or password")#shows error message

window=Tk()

window.geometry("1280x700+0+0")#size of window
#window.resizable(False,False)#prevents resizing of window

#backgroundImage = ImageTk.PhotoImage(file=str(IMAGE_DIR / "bg.jpeg"))#background image
#bglabel=Label(window,image=backgroundImage)
#bglabel.place(x=0,y=0)#places background image

loginFrame=Frame(window)
loginFrame.place(x=400,y=150)#places login frame

logoImage=PhotoImage(file=str(IMAGE_DIR / "logo.png"))#logo image
logoLabel=Label(loginFrame,image=logoImage)
logoLabel.grid(row=0,column=0,columnspan=2,pady=10,padx=5)#places logo image

usernameImage=PhotoImage(file=str(IMAGE_DIR / "user.png"))#user image
usernameLabel=Label(loginFrame,image=usernameImage,text="Username",compound=LEFT,font=("times new roman",15,"bold"))#creates username label with image
usernameLabel.grid(row=1,column=0,pady=10,padx=10)#places username label

usernameEntry=Entry(loginFrame,font=("times new roman",12,"bold"),bd=5,fg="black")#creates username entry
usernameEntry.grid(row=1,column=1,pady=10,padx=10)#places username entry

passwordImage=PhotoImage(file=str(IMAGE_DIR / "padlock.png"))#password image
passwordLabel=Label(loginFrame,image=passwordImage,text="Password",compound=LEFT,font=("times new roman",15,"bold"))#creates password label with image
passwordLabel.grid(row=2,column=0,pady=10,padx=10)#places password label

passwordEntry=Entry(loginFrame,font=("times new roman",12,"bold"),bd=5,fg="black",show="*")#creates password entry
passwordEntry.grid(row=2,column=1,pady=10,padx=10)#places password entry

loginButton=Button(loginFrame,text="Login",font=("times new roman",15,"bold"),bd=5,fg="white",bg="cornflowerblue",width=12,activebackground="cornflowerblue",activeforeground="white",cursor="hand2",
                   command=login)#creates login button
loginButton.grid(row=3,column=1,columnspan=2,pady=10,padx=10)#creates login button





window.mainloop()#keeps window open 
