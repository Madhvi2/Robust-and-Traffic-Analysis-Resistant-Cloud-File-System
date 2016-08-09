'''
Created on Jul 17, 2012

@author: madhvi
'''
import login
from login import *
from Tkinter import *
from tkFileDialog import askopenfilename
import sys
import re
import os.path
import getopt
import getpass
import gdata.docs.service
import gdata.docs.data
import gdata.docs.client
import M2Crypto
import mimetypes
from M2Crypto import EVP
from random import choice
from random import randint
import base64
import gdata.sample_util 
from random import choice
from random import randint
from sympy import Symbol, Rational, binomial,factorial
from sympy.solvers import solve
from passlib.hash import pbkdf2_sha512
import random
"""
class DocsSample(object):
    def __init__(self, email, password):
        source = 'my_application' 
        self.gd_client = gdata.docs.service.DocsService()
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.source = 'Document List Python Sample'
        self.gd_client.ProgrammaticLogin()
        self.client = gdata.docs.client.DocsClient(source=source)
        self.client.ssl = True  # Force all API requests through HTTPS
        self.client.http_client.debug = False  # Set to True for debugging HTTP requests
        self.client.ClientLogin(email, password, source=source)
        self.convert=False

                

class MyApp:
        def __init__(self, parent):
                self.myParent = parent   
                mc1 = self.myContainer1 = Frame(parent)

                self.myContainer1.pack()
                self.var1 = StringVar()
                self.var2 = StringVar()
                
                R1 = Radiobutton(self.myContainer1, text="List", variable=self.var1, value="List")
                R1.pack( anchor = W )
                R2 = Radiobutton(self.myContainer1, text="Format", variable=self.var1, value="Format")
                R2.pack( anchor = W )

                self.LabelStore = Label(self.myContainer1, text="Storage:")
                self.LabelStore.pack(side=TOP,padx=10,pady=10)
                self.entryStore = Entry(self.myContainer1, width=10)
                self.entryStore.pack(side=TOP,padx=10,pady=10)

                R3 = Radiobutton(self.myContainer1, text="Upload", variable=self.var2, value="Upload")
                R3.pack( anchor = W)
                R4 = Radiobutton(self.myContainer1, text="Download", variable=self.var2, value="Download")
                R4.pack( anchor = W)

                self.LabelPWD = Label(self.myContainer1, text="Filename:")
                self.LabelPWD.pack(side=TOP, padx=5, pady=5)
                self.entryFile = Entry(self.myContainer1, width=10)
                self.entryFile.pack(side=TOP,padx=10,pady=10)

                self.button1 = Button(self.myContainer1, command=self.button1Click)  
                self.button1.configure(text="Submit")
                self.button1.pack(side=TOP)
                self.button1.focus_force()

                self.button2 = Button(self.myContainer1, command=self.browseClick)
                self.button2.configure(text="Browse")
                self.button2.pack(side=TOP)
                
                
        def button1Click(self):  ### (2)
                #print "button1Click event handler"
                
                storage = self.entryStore.get()
                filename = self.entryFile.get()
                rad1Val = self.var1.get()
                rad2Val = self.var2.get()
                try:
                    #self.metadatasecurity()
                    while True:
                        #self._PrintMenu()
                        #choice = self._GetMenuChoice(7)
                        if rad1Val == 1:
                            print "1"
                            #self._ListAllDocuments()
                        elif rad1Val == 2:
                            print "2"
                            #self._FormatDocuments()
                        elif rad2Val == 3:
                            print "3"
                            #self._UploadMenu()
                        elif rad2Val == 4:
                            print "4"
                            #file_nm = ''
                            #file_nm = raw_input('Enter the file name to be downloaded')
                            #self.GDocDownload(file_nm)
                        elif choice == 5:
                            return
                except KeyboardInterrupt:
                    print '\nGoodbye.'
                    return

            


                print "List/Format: ", rad1Val
                print "storage: ", storage              
                print "Up/Download: ",rad2Val
                print "filename: ",filename
        
        def button2Click(self): ### (2)
                print "button2Click event handler"
                #self.entryUN.set() = " "
                #self.entryPWD.set() = " "
                #self.myParent.destroy()

        def browseClick(self):
                filename = askopenfilename(filetypes=[("allfiles","*"),("pythonfiles","*.py")])
                tmp = filename.replace("/","\\")
                print "File:",tmp
                self.entryFile.delete(0,len(self.entryFile.get()))
                self.entryFile.config(width=len(tmp)+5)
                self.entryFile.insert(0,tmp)
"""                
root = Tk()
root.title("Menu Form")
myapp = MyApp(root)
root.mainloop()
#onj=MyApp(root)
print myapp.button1Click()

