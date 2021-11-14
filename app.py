from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.font import Font
from TkinterDnD2 import *
from sys import argv
import os
import chardet
import configparser

martextPath = __file__+"\\..\\"

Config = configparser.ConfigParser()
Config.read(martextPath+"data\\config.ini")

window = TkinterDnD.Tk()
window.iconbitmap(martextPath+"imgs\\paperfeatherAllSizes.ico")
window.title("MartText")
window.geometry("1280x720+200+200")

appTitle = "MarText"
appTitleSeparator = " - "
appFont = Font(family="Helvetica", size = 16)
appZoom = IntVar()
fileName = "New Text File"
filePath = ""
fileTypes = (("Text Files", "*.txt"), ("HTML Files", "*.html, *.htm"), ("CSS Files", "*.css"),
("Javascript Files", "*.js"), ("Python Files", "*.py, *.pyw"),("Lua Files", "*.lua"),
("Markdown", "*.markdown *.md *.mdtext"), ("All Files", "*.*"))
fileEncoding = StringVar(value="utf-8")
global selected
selected = False
nightModeOn = BooleanVar(value=Config.get("Options", "NightMode"))
wordWrapOn = IntVar(value=0)


def update_title():
    window.title(fileName+appTitleSeparator+appTitle)

def drop(event):
    if event.data:
        if textBox.edit_modified():
            response = messagebox.askyesnocancel("Are you sure?", "Do you want to close the current file without saving?", default="no", icon="warning")
            if(response == True):
                open_file(event.data)
            elif(response == None):
                #cancel
                pass
            else:
                saved = save_file()
                if saved:
                    open_file(event.data)
        else:
            open_file(event.data)

def get_file_encoding(path):
    #Open in binary mode to check encoding
    file = open(path, "rb")
    if(not file.readable()):
        messagebox.showerror("Error while opening file", "Unable to read file contents.")
        return False
    content = file.read()
    encoding = chardet.detect(content)["encoding"]
    file.close()
    return encoding

def check_file_exists(path):
    if(os.path.exists(path)):
        return True
    else:
        messagebox.showerror("Error", "File or Directory does not exist.")
        return False

def new_file(e=False):
    if(e and textBox.edit_modified()):
        response = messagebox.askyesnocancel("Are you sure?", "Do you want to close the current file without saving?", default="no", icon="warning")
        if response == False:
            saved = save_file()
            if not saved:
                return False
        elif response == None:
            return False
    global filePath
    global fileName
    textBox.delete("1.0", END)
    #reset undo redo stack
    textBox.edit_modified(False)
    statusLabel.config(text="New File")
    filePath = ""
    fileName = "New Text File"
    fileEncoding.set("utf-8")
    update_title()

def open_file(path):
    global filePath
    global fileName
    global fileTypes
    global fileEncoding
    if(check_file_exists(path) == False):
        #new_file()
        return
    filePath = path
    fileName = os.path.basename(filePath)
    statusLabel.config(text=filePath)
    update_title()

    #Get encoding
    encoding = get_file_encoding(filePath)
    if encoding == False:
        new_file()
        return False

    fileEncoding.set(encoding)
    #Open text file
    text_file = open(filePath, "r", encoding=encoding)
    
    content = text_file.read()
    
    textBox.delete("1.0", END)
    textBox.insert(END, content)
    #reset undo redo stack
    textBox.edit_modified(False)
    text_file.close()
    return True

def open_file_prompt(e):
    #Grab File Name
    text_file = filedialog.askopenfilename(initialdir="Documents", title="Open File", filetypes=fileTypes)
    if not text_file:
        return False
    return open_file(text_file)

def save_file(e = False):
    global filePath
    global fileName
    global fileEncoding
    if filePath:
        #save the file
        text_file = open(filePath, 'w', encoding=fileEncoding.get())
        text_file.write(textBox.get(1.0, END))
        text_file.close()
        return True
    else:
        return save_as_file()
    return False

def save_as_file(e = False):
    global filePath
    global fileName
    global fileTypes
    global fileEncoding
    text_file = filedialog.asksaveasfilename(defaultextension=".*", initialdir="Documents", title="Save File as",
    filetypes=fileTypes)
    if not text_file:
        return False
    filePath = text_file
    fileName = os.path.basename(filePath)
    statusLabel.config(text=filePath)
    update_title()
    #save the file
    text_file = open(filePath, 'w', encoding=fileEncoding.get())
    text_file.write(textBox.get(1.0, END))
    text_file.close()
    return True

def exit_program():
    if textBox.edit_modified():
        response = messagebox.askyesnocancel("Are you sure?", "Do you want to quit without saving?", default="no", icon="warning")
        if(response == True):
            #Quit without saving
            pass
        elif(response == None):
            #Don't quit
            return False
        else:
            saved = save_file()
            if not saved:
                return False
    configFile = open(martextPath+"data\\config.ini", "w")
    Config.set("Options", "NightMode", str(nightModeOn.get()))
    Config.write(configFile)
    configFile.close()
    window.quit()

def cut_text(e):
    global selected
    if e:
        selected = window.clipboard_get()
    elif textBox.selection_get():
        selected = textBox.selection_get()
        textBox.delete("sel.first", "sel.last")
        window.clipboard_clear()
        window.clipboard_append(selected)

def copy_text(e):
    global selected
    #check to see if we used keyboard shortcuts
    if e:
        selected = window.clipboard_get()
    elif textBox.selection_get():
        selected = textBox.selection_get()
        window.clipboard_clear()
        window.clipboard_append(selected)

def paste_text(e):
    global selected
    if e:
        selected = window.clipboard_get()
    elif selected:
        position = textBox.index(INSERT)
        textBox.insert(position, selected)

def select_all(e=False):
    textBox.tag_add("sel", "1.0", END)

def clear_all():
    textBox.delete(1.0, END)

def popup_edit_menu(e):
    editMenu.tk_popup(e.x_root, e.y_root)

def finder_gained_focus(e):
    if finderEntry.get() == "Find":
        finderEntry.delete("1.0", END)

def finder_lost_focus(e):
    if not finderEntry.get():
        finderEntry.insert("0", "Find")

def finder_close(e=False):
    finderFrame.pack_forget()

def finder_open(e=False):
    finderFrame.pack(side=RIGHT, anchor=N)
    finderEntry.focus()

def finder_find_in_file(direction):
    #direction can also be an event
    pos = textBox.search(pattern=textBox.get("1.0", END), backwards=(direction == N), index=textBox.index(INSERT))
    print(pos)

#def find():
     
    # remove tag 'found' from index 1 to END
    #text.tag_remove('found', '1.0', END)
     
    # returns to widget currently in focus
    #s = edit.get()
     
    #if (s):
        #idx = '1.0'
        #while 1:
            # searches for desired string from index 1
            #idx = text.search(s, idx, nocase = 1,
                            #stopindex = END)
             
            #if not idx: break
             
            # last index sum of current index and
            # length of text
            #lastidx = '% s+% dc' % (idx, len(s))
             
 
            # overwrite 'Found' at idx
            #text.tag_add('found', idx, lastidx)
            #idx = lastidx
 
        # mark located string as red
         
        #text.tag_config('found', foreground ='red')
    #edit.focus_set()
    

def toggle_night_mode():
    primary = "#282b30" #textbox color
    secondary = "#1e2124"
    textcolor = "#ffffff"
    textcolor2 = "#347751"
    if(nightModeOn.get() == False):
        primary = "white"
        secondary = "gainsboro"
        textcolor = "black"
        textcolor2 = "black"
    window.config(bg=primary)
    statusFrame.config(bg=secondary)
    for slave in statusFrame.slaves():
        slave.configure(bg=secondary, fg=textcolor2)
    finderFrame.configure(bg=secondary)
    #for slave in finderFrame.slaves():
    #    slave.configure(bg=secondary)
    finderEntry.configure(bg=primary, fg=textcolor)
    finderDown.configure(bg=secondary, fg=textcolor2)
    finderUp.configure(bg=secondary, fg=textcolor2)
    finderClose.configure(bg=secondary, fg=textcolor2)
    mainFrame.config(bg=primary)
    textBox.config(bg=primary, fg=textcolor, insertbackground=textcolor2)
    fileMenu.config(bg=secondary, fg=textcolor, selectcolor=textcolor)
    editMenu.config(bg=secondary, fg=textcolor, selectcolor=textcolor)
    optionsMenu.config(bg=secondary, fg=textcolor, selectcolor=textcolor2)

def toggle_word_wrap():
    if(wordWrapOn == 0):
        textBox.configure(wrap="none", xscrollcommand=textScrollHorizontal.set)
        textScrollHorizontal.config(command=textBox.xview)
    else:
        textBox.configure(wrap="word")

def zoom(num):
    appFont.configure(size=num)
    pass 

#Main Frame
mainFrame = Frame(window)
mainFrame.pack(pady=0, expand=True, fill=BOTH)

#Vertical Scroll Bar
textScroll = Scrollbar(mainFrame)
textScroll.pack(side=RIGHT, fill=Y)

#Horizontal Scroll Bar
textScrollHorizontal = Scrollbar(mainFrame, orient="horizontal")
textScrollHorizontal.pack(side=BOTTOM, fill=X)

#Text Box
textBox = Text(mainFrame, width=97, height=25, undo=True, wrap="none",
yscrollcommand=textScroll.set, xscrollcommand=textScrollHorizontal.set,
font=appFont, selectbackground="yellow", selectforeground="black",
insertwidth=4, tabs="1c")
textBox.drop_target_register(DND_TEXT, DND_FILES)
textBox.dnd_bind('<<Drop>>', drop)
textBox.pack(expand=True, fill=BOTH)

#Frame
finderFrame = Frame(textBox, cursor="arrow")

finderEntry = Entry(finderFrame, width=32)
finderEntry.insert(0, "Find")
finderEntry.grid(columnspan=3)
finderEntry.bind("<FocusIn>", finder_gained_focus)
finderEntry.bind("<FocusOut>", finder_lost_focus)
finderEntry.bind("<Escape>", finder_close)
finderEntry.bind("<Return>", finder_find_in_file)

finderUp = Button(finderFrame, text="↑", height=1, relief=FLAT)
finderUp.grid(row=1, column=0, sticky="we")

finderDown = Button(finderFrame, text="↓", relief=FLAT)
finderDown.grid(row=1, column=1, sticky="we")

finderClose = Button(finderFrame, text="×", relief=FLAT, command=finder_close)
finderClose.grid(row=1, column=2, sticky="news")

#config scrollbar
textScroll.config(command=textBox.yview)
textScrollHorizontal.config(command=textBox.xview)

statusFrame = Frame(window)
statusFrame.pack(expand=False, fill=X)

statusLabel = Label(statusFrame, text="Ready", height=1)
statusLabel.pack(side=RIGHT)

statusEncoding = Label(statusFrame, height=1, textvariable=fileEncoding)
statusEncoding.pack(side=RIGHT)

#statusZoom = Scale(statusFrame, orient="horizontal", from_=10, to=30, command=zoom, showvalue=False, variable=appZoom)
#statusZoom.pack(side=LEFT)

#Menus
#file menu
menu = Menu(window)
window["menu"] = menu
fileMenu = Menu(window)
menu.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="New", command=lambda: new_file(True), accelerator="(Ctrl+N)")
fileMenu.add_command(label="Open", command=lambda: open_file_prompt(False), accelerator="(Ctrl+O)")
fileMenu.add_command(label="Save", command=lambda: save_file(False), accelerator="(Ctrl+S)")
fileMenu.add_command(label="Save as", command=lambda: save_as_file(False), accelerator="(Ctrl+Shift+S)")
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=exit_program)
#edit menu
editMenu = Menu(window)
menu.add_cascade(menu=editMenu, label="Edit")
editMenu.add_command(label="Undo", command=textBox.edit_undo, accelerator="(Ctrl+Z)")
editMenu.add_command(label="Redo", command=textBox.edit_redo, accelerator="(Ctrl+Y)")
editMenu.add_separator()
editMenu.add_command(label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+X)")
editMenu.add_command(label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+C)")
editMenu.add_command(label="Paste", command=lambda: paste_text(False), accelerator="(Ctrl+V)")
editMenu.add_separator()
editMenu.add_command(label="Select All", command=lambda: select_all(False), accelerator="(Ctrl+A)")
editMenu.add_command(label="Find", command=lambda: finder_open(False), accelerator="(Ctrl+F)")
editMenu.add_command(label="Clear", command=lambda: clear_all())
#options menu
optionsMenu = Menu(window, tearoff=False)
menu.add_cascade(menu=optionsMenu, label="Options")
optionsMenu.add_checkbutton(label="Night Mode", command=toggle_night_mode, variable=nightModeOn)
#optionsMenu.add_checkbutton(label="Word Wrap", command=toggle_word_wrap, variable=wordWrapOn)

#Edit Bindings
window.bind("<Control-x>", cut_text)
window.bind("<Control-c>", copy_text)
window.bind("<Control-v>", paste_text)
window.bind("<Control-n>", new_file)
window.bind("<Control-o>", open_file_prompt)
window.bind("<Control-s>", save_file)
window.bind("<Control-S>", save_as_file)
window.bind("<Control-a>", select_all)
window.bind("<Control-f>", finder_open)
textBox.bind("<Button-3>", popup_edit_menu)
#window.bind("<Control-+>", zoom)

#apply night mode before opening file
toggle_night_mode()

if(argv and len(argv) > 1):
    open_file(argv[1])
else:
    new_file()

window.protocol("WM_DELETE_WINDOW", exit_program)
window.mainloop()