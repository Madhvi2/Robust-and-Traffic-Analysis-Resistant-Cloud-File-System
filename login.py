'''
Created on Jul 16, 2012

@author: madhvi
'''
#import print_menu
from Tkinter import *
from tkFileDialog import askopenfilename
import tkMessageBox
import sys
import re
import os.path
import getopt
import getpass
import gdata.docs.service
import gdata.docs.data
import gdata.docs.client
import gdata.apps.service
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

DECODE = 0
ENCODE =1


def truncate(content, length=15, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length] + suffix
# Checks for if file exists in google docs or not and if is not there generate a 4 bit random code for a file. 
def Generatecode(filename,value):
    flag=False
    if(os.path.exists("file_info.txt")):
        temp_file=open("file_info.txt","r")
        content=temp_file.read()
        temp_file.close()
        content=content.split("\n")
        content=content[:-1]
        list_choice=[]
        for item in content:
            temp_data=item.split(":")[1]
            list_choice.append(temp_data) 
        for item in content:
            temp_data=item.split(":")[1]
            temp_file =item.split(":")[0]
            if(filename==temp_file):
                flag= True
        while(True):
            ch_number=randint(1000,9999)
            occ=list_choice.count(ch_number)
            #print "occ:" + str(occ)
            if(occ==0):
                break    
        f_info=open("file_info.txt","a")
        f_info.write(filename.split(".")[0])
        f_info.write(":")
        f_info.write(str(ch_number))
        f_info.write(":")
        f_info.write(str(int(value)))
        f_info.write("\n")
        f_info.close()
    else:
        f_info=open("file_info.txt","w")
        f_info.write(filename.split(".")[0])
        f_info.write(":")
        ch_number=randint(1000,9999)
        #print "ch_number" + str(ch_number)
        f_info.write(str(ch_number))
        f_info.write(":")
        f_info.write(str(int(value)))
        f_info.write("\n")
        f_info.close() 
    if(flag==True):
        #print "File already exists in google docs"
        #sys.exit()
        
        tkMessageBox.showinfo("Message","File already exists in google docs")
    return ch_number             

# Check the occurrence of files in google docs.             
        
def filesearch_download(filename):
    flag=False
    temp_file=open("file_info.txt","r")
    content=temp_file.read()
    temp_file.close()
    content=content.split("\n")
    content=content[:-1]
    for item in content:
        temp_data=item.split(":")[1]
        temp_filename=item.split(":")[0].split(".")[0]
        if(temp_filename==filename):
            flag=True
    if(flag==False):
        tkMessageBox.showinfo("Message","No such file exists in google docs")
        #print "No such file exists in google docs."
        #sys.exit()

# Checks if there are sufficient dummy block to upload file.   
def availability(numchunks):
    f = open("info_dummy.txt","r")
    aa = f.read()
    a = aa.split(",")
    a=a[:-1]
    count=0
    for i in range(len(a)):
        # print str(a[i].split(":")[1])
        if(int(a[i].split(":")[1])== 0):
            count = count +1
    if(numchunks>count):
        tkMessageBox.showinfo("Message","Not sufficient space on google docs")
        #print "Not sufficient space on google docs"
        #sys.exit()   

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
    
    def _PrintFeed(self, feed):
        if not feed.entry:
            print 'No entries in feed.\n'
        for i, entry in enumerate(feed.entry):
            print '%s %s\n' % (i+1, entry.title.text.encode('UTF-8'))

# Upload the files to google docs.
    def _UploadMenu(self,filepath):
        
        #Encryption of files. 
        
        key = M2Crypto.Rand.rand_bytes(32)
        salt = M2Crypto.Rand.rand_bytes(8)
        iv = '\0' * 32
        list_file=filepath.split("\\")
        filename=list_file.pop()
        f1= open(filename,"r")
        buffer = f1.read()
        cipher = EVP.Cipher('aes_128_cbc', key=key, iv=iv, op=1)
        p = filename.split('.')[0]
        encrypt_file = 'encrypt' + '_' + p + '.' + '.txt'
        fin = open(encrypt_file,"w")
        fin.write(cipher.update(buffer))
        fin.write(cipher.final())
        fin.close()
        fsize = os.path.getsize(encrypt_file)
        additional=fsize%256000 
        additional_numchunks= 256000-additional
        fin1 = open(encrypt_file,"a")
        fin1.write("::::")
        for i in range(1,additional_numchunks/2+1-2):
                fin1.write('&&')
        fin1.close()
        fsize1 = os.path.getsize(encrypt_file)
        numchunks=int(fsize1)/256000
        chunksize = int(float(fsize1)/float(numchunks))
        total_bytes = fsize1
        chunksz = chunksize
        
        
        #check for space in Google Docs.
        counter_i=2
        while(True):
            previous_chunk=counter_i*numchunks
            value= binomial(previous_chunk,numchunks)
            #print value
            if(value>=100):
                break
            counter_i = counter_i + 1
        counter_j=counter_i-1
        k = 0.1
        while(True):
            sum_value=binomial(counter_j+k*numchunks,numchunks)
            if(sum_value>=100):
                break
            else:
                k = k + 0.1
        value=counter_j+k*numchunks
        bname2= str(Generatecode(filename,value))
        f_file=open("file_info.txt","r")
        file_content=f_file.read()
        file_content=file_content.split("\n")
        file_content=file_content[:-1]
        f_file.close()
        #print file_content
        list_additional=[]
        for ele in file_content:
            temp_ele=ele.split(":")
            list_additional.append(int(temp_ele[2]))
        list_additional.sort()
        element= list_additional.pop()
        if(element>=value):
                if(numchunks%2==0):
                    availability(2*numchunks+element)
                else:
                    availability(2*numchunks+3+element)
        else:
                if(numchunks%2==0):
                    availability(2*numchunks+value)
                else:
                    availability(2*numchunks+3+value)

        # Splitting of files into equal parts.
         
        f3=open(encrypt_file,"r")
        
        for x in range(numchunks):
            chunkfilename = bname2 + "_"+str(x+1) + '.txt' 
            data = f3.read(chunksz)
            total_bytes += len(data)
            chunkf = file(chunkfilename, 'w')
            chunkf.write(data)
            chunkf.close()
        f3.close()
        for x in range(numchunks):
            chunkfilename = bname2 + "_"+str(x+1) + "_base64"+'.txt' 
            file_name=bname2 + "_"+str(x+1) +'.txt' 
            f1 = open(file_name,"r")
            ad= f1.read()
            f2 = open(chunkfilename,"w")
            f2.write(base64.b64encode(ad))
            f1.close()
            f2.close()  

        bname3= bname2
        
        # Upload files to Google docs.
        def uploadfunction(filechunk):
            
            f_newfile =open("blockfile.txt","a")
            f = open ("info_dummy.txt","r")
            aa = f.read()
            f.close()
            a = aa.split(",")
            a=a[:-1]
            t= []
            for i in range(len(a)):
                s = a[i].split(":")
                if(int(s[1])==0):
                        t.append(int(s[0]))
            block_number = choice(t)
            f.close()
            for ele in range(len(a)):
                c = a[ele].split(":")
                if(int(block_number)==int(c[0])):
                    if(int(c[1])==0):                        
                        file_name = filechunk
                        file_path = os.path.realpath(file_name)
                        type = mimetypes.guess_type(file_path)
                        title = str(block_number)
                        temporary=file_name.split("_")
                        if(len(temporary)==4):
                                f_newfile.write((temporary[0]+"_"+temporary[1])+temporary[2])
                                f_newfile.write(":")
                                f_newfile.write(str(block_number))
                                f_newfile.write("\n")
                        else:
                                f_newfile.write((temporary[0]+"_"+temporary[1]))
                                f_newfile.write(":")
                                f_newfile.write(str(block_number))
                                f_newfile.write("\n")
                        ms = gdata.MediaSource(file_path = file_path,content_type = type[0])
                        feed = self.client.GetDocList(uri='/feeds/default/private/full/-/document')
                        for entry in feed.entry:
                                    if (entry.title.text.encode('UTF-8') == str(block_number)):
                                        self.client.Delete(entry)
                                        entry1 = self.gd_client.Upload(ms,title)
                                        #entry1 = self.gd_client.Upload(ms,title)
                                        link =  entry.GetAlternateLink().href
                                        u = link.split('/')
                                        s.append(u[5])
                                        
                        fin2 = open("info_dummy.txt","w")
                        for j in range(len(a)):
                            e = a[j].split(":")
                            if(int(e[0]) == int(block_number)):
                                new=str(e[0])+":1"
                                fin2.write(new)
                                fin2.write(",")                                                    
                            else:
                                fin2.write(e[0] + ":" + e[1])
                                fin2.write(",") 
            fin2.close()
            f_newfile.close()
            return s  
        
        for i in range(1,numchunks+1):
            filechunk= bname3+ "_"+ str(i) + "_base64.txt"
            sw = uploadfunction(filechunk)
        fin1 = open("info1.txt","ab")
        fin1.write(bname3+":" + str(numchunks)+"::::::")
        for ele in sw:
            fin1.write(ele+ ",")
            #print "Ele:" + ele
        fin1.write('::::::' +base64.b64encode(key))
        fin1.write("\n\n\n\n")
        fin1.close()
         
        # Generating xor of files.
        
        def xorfunction(num_chunk):
            
            #xor for chunks consecutive pairwise
            
            count1 =1
            count2=2 
            for i in range(num_chunk/2):
                
                f_file1=open((bname3+"_"+ str(count1)+".txt"),"rb")
                s=f_file1.read()
                f_file1.close()
                f_file2=open((bname3+"_"+ str(count2)+".txt"),"rb")
                u=f_file2.read()
                f_file2.close()
                f5=open((bname3+"_"+ str(count1)+ "x"+str(count2)+".txt"),"wb")
                for i in range(len(s)):
                    string12 = chr(ord(s[i])^ord(u[i]))
                    f5.write(string12)
                f5.close()
                f_ch=open((bname3+"_"+str(count1)+"x"+str(count2)+".txt"),"rb")
                f_64=open((bname3+"_"+str(count1)+"x"+str(count2)+"_base64.txt"),"wb")
                v = f_ch.read()
                w=base64.b64encode(v)
                f_64.write(w)
                f_ch.close()
                f_64.close()
                filechunk= bname3+"_"+str(count1)+"x"+str(count2)+"_base64.txt"
                sum=uploadfunction(filechunk)
                count1=count1+2
                count2=count2+2
 
            
        if(numchunks%2==0):
            num_chunk=numchunks
            xorfunction(num_chunk)   
           
        else:
            num_chunk=numchunks+1
            f=open((bname3+"_"+ str(numchunks)+".txt"),"rb")
            ab=f.read()
            f.close()
            f=open((bname3+"_"+ str(numchunks+1)+".txt"),"wb")
            size_complement= os.path.getsize((bname3+"_"+ str(numchunks)+".txt"))
            for i in range(size_complement):
                f.write("0")
            f.close()
            size_confirm =os.path.getsize((bname3+"_"+ str(numchunks+1)+".txt"))
            f2=open((bname3+"_"+ str(numchunks+1)+".txt"),"rb")
            cd = f2.read()
            f2.close()
            f_temp=open("temp_file.txt","a")
            f_temp.write((bname3+"_"+ str(numchunks+1)))
            f_temp.close()
            xorfunction(num_chunk)
        
        # Xor of files which are separated by a single chunk. 
        if(num_chunk%4==0):
            count1=1
            count2=3    
            for i in range(1,num_chunk/2):
                if(os.path.exists((bname3+"_"+ str(count1)+".txt"))):
                    f_file1 =open((bname3+"_"+ str(count1)+".txt"),"rb")
                    s=f_file1.read()
                    f_file1.close()
                    f_file2=open((bname3+"_"+ str(count2)+".txt"),"rb")
                    u=f_file2.read()
                    f_file2.close()
                    f5=open((bname3+"_"+str(count1)+"x"+str(count2)+".txt"),"wb")
                    for i in range(len(s)):
                        string12 = chr(ord(s[i])^ord(u[i]))
                        f5.write(string12)
                    f5.close()
                    f_ch=open((bname3+"_"+str(count1)+"x"+str(count2)+".txt"),"rb")
                    f_64=open((bname3+"_"+str(count1)+"x"+str(count2)+"_base64.txt"),"wb")
                    v = f_ch.read()
                    w=base64.b64encode(v)
                    f_64.write(w)
                    f_ch.close()
                    f_64.close()
                    filechunk=bname3+"_"+str(count1)+"x"+str(count2)+"_base64.txt"
                    sum = uploadfunction(filechunk)
                    count1 = count1 +4
                    count2 = count2 +4
                    
                # xoring of 2,4 and 5,7
            count3=2
            count4=4    
            for i in range(num_chunk/2):
                if(os.path.exists((bname3+"_"+ str(count3)+".txt"))):
                    f_file1 =open((bname3+"_"+ str(count3)+".txt"),"rb")
                    s=f_file1.read()
                    f_file1.close()
                    f_file2=open((bname3+"_"+ str(count4)+".txt"),"rb")
                    u=f_file2.read()
                    f_file2.close()
                    f5=open((bname3+"_"+str(count3)+"x"+str(count4)+".txt"),"wb")
                    for i in range(len(s)):
                        string12 = chr(ord(s[i])^ord(u[i]))
                        f5.write(string12)
                    f5.close()
                    f_ch=open((bname3+"_"+str(count3)+"x"+str(count4)+".txt"),"rb")
                    f_64=open((bname3+"_"+str(count3)+"x"+str(count4)+"_base64.txt"),"wb")
                    v = f_ch.read()
                    w=base64.b64encode(v)
                    f_64.write(w)
                    f_ch.close()
                    f_64.close()
                    filechunk= bname3+"_"+str(count3)+"x"+str(count4)+"_base64.txt"
                    sum = uploadfunction(filechunk)
                    count3 = count3 +4
                    count4 = count4 +4
                else:
                    break
            
        else:
            temp_num=num_chunk/2
            temp_chunk=(num_chunk-temp_num-1)*2
            count1=1
            count2=3  
            for i in range(temp_chunk/2-1):
                if(os.path.exists((bname3+"_"+ str(count1)+".txt"))and os.path.exists(bname3+"_"+ str(count2)+".txt")):
                    f_file1 =open((bname3+"_"+ str(count1)+".txt"),"rb")
                    s=f_file1.read()
                    f_file1.close()
                    f_file2=open((bname3+"_"+ str(count2)+".txt"),"rb")
                    u=f_file2.read()
                    f_file2.close()
                    f5=open((bname3+"_"+str(count1)+"x"+str(count2)+".txt"),"wb")
                    for i in range(len(s)):
                        string12 = chr(ord(s[i])^ord(u[i]))
                        f5.write(string12)
                    f5.close()
                    f_ch=open((bname3+"_"+str(count1)+"x"+str(count2)+".txt"),"rb")
                    f_64=open((bname3+"_"+str(count1)+"x"+str(count2)+"_base64.txt"),"wb")
                    v = f_ch.read()
                    w=base64.b64encode(v)
                    f_64.write(w)
                    f_ch.close()
                    f_64.close()
                    filechunk=bname3+"_"+str(count1)+"x"+str(count2)+"_base64.txt"
                    sum =uploadfunction(filechunk)
                    count1 = count1 +4
                    count2 = count2 +4
                
                # xoring of 2,4 and 5,7
            count3=2
            count4=4    
            for i in range(temp_chunk/2-1):
                if(os.path.exists((bname3+"_"+ str(count3)+".txt"))and os.path.exists(bname3+"_"+ str(count4)+".txt")):
                    f_file1 =open((bname3+"_"+ str(count3)+".txt"),"rb")
                    s=f_file1.read()
                    f_file1.close()
                    f_file2=open((bname3+"_"+ str(count4)+".txt"),"rb")
                    u=f_file2.read()
                    f_file2.close()
                    f5=open((bname3+"_"+str(count3)+"x"+str(count4)+".txt"),"wb")
                    for i in range(len(s)):
                        string12 = chr(ord(s[i])^ord(u[i]))
                        f5.write(string12)
                    f5.close()
                    f_ch=open((bname3+"_"+str(count3)+"x"+str(count4)+".txt"),"rb")
                    f_64=open((bname3+"_"+str(count3)+"x"+str(count4)+"_base64.txt"),"wb")
                    v = f_ch.read()
                    w=base64.b64encode(v)
                    f_64.write(w)
                    f_ch.close()
                    f_64.close()
                    filechunk=bname3+"_"+str(count3)+"x"+str(count4)+"_base64.txt"
                    sum = uploadfunction(filechunk)
                    count3 = count3 +4
                    count4 = count4 +4
                else:
                    break
            
                # complement of two left chunks
            counter1= count4-3
            f_file1=open((bname3+"_"+str(counter1)+".txt"),"rb")
            ab=f_file1.read()
            f_file1.close()
            f=open((bname3+"_"+ str(counter1)+"_c"+".txt"),"wb")
            size_complement= os.path.getsize((bname3+"_"+ str(counter1)+".txt"))
            for i in range(size_complement):
                f.write("0")
            f.close()
            size_confirm =os.path.getsize((bname3+"_"+ str(counter1+1)+".txt"))
            f_file2=open((bname3+"_"+str(counter1+1)+".txt"),"rb")
            ab=f_file2.read()
            f_file2.close()
            f=open((bname3+"_"+ str(counter1+1)+"_c"+".txt"),"wb")
            size_complement= os.path.getsize((bname3+"_"+ str(counter1+1)+".txt"))
            for i in range(size_complement):
                f.write("0")
            f.close()
            size_confirm =os.path.getsize((bname3+"_"+ str(counter1+1)+".txt"))
            
            # xor of two left file with complement of other left one.
            f_file1=open((bname3+"_"+str(counter1)+".txt"),"rb")
            s=f_file1.read()
            f_file1.close()
            f_file2=open((bname3+"_"+str(counter1+1)+"_c"+".txt"),"rb")
            u=f_file2.read()
            f_file2.close()
            f5=open((bname3+"_"+str(counter1)+"x"+str(counter1+1)+"_c"+".txt"),"wb")
            for i in range(len(s)):
                string12 = chr(ord(s[i])^ord(u[i]))
                f5.write(string12)
            f5.close()
            f_ch=open((bname3+"_"+str(counter1)+"x"+str(counter1+1)+"_c"+".txt"),"rb")
            f_64=open((bname3+"_"+str(counter1)+"x"+str(counter1+1)+"_c"+"_base64.txt"),"wb")
            v = f_ch.read()
            w=base64.b64encode(v)
            f_64.write(w)
            f_ch.close()
            f_64.close()
            filechunk=bname3+"_"+str(counter1)+"x"+str(counter1+1)+"_c"+"_base64.txt"
            sum = uploadfunction(filechunk)
    
            f_file1=open((bname3+"_"+str(counter1+1)+".txt"),"rb")
            s=f_file1.read()
            f_file1.close()
            f_file2=open((bname3+"_"+str(counter1)+"_c"+".txt"),"rb")
            u=f_file2.read()
            f_file2.close()
            f5=open((bname3+"_"+str(counter1+1)+"x"+str(counter1)+"_c"+".txt"),"wb")
            for i in range(len(s)):
                string12 = chr(ord(s[i])^ord(u[i]))
                f5.write(string12)
            f5.close()
            f_ch=open((bname3+"_"+str(counter1+1)+"x"+str(counter1)+"_c"+".txt"),"rb")
            f_64=open((bname3+"_"+str(counter1+1)+"x"+str(counter1)+"_c"+"_base64.txt"),"wb")
            v = f_ch.read()
            w=base64.b64encode(v)
            f_64.write(w)
            f_ch.close()
            f_64.close()
            filechunk=bname3+"_"+str(counter1+1)+"x"+str(counter1)+"_c"+"_base64.txt"
            sum = uploadfunction(filechunk)
            print "done wid upload of functuion"
            
            #additiona number of uploads
        """    
        print "time to upload some additional chunk"
        f_dummy=open("info_dummy.txt","r")
        dummy_content= f_dummy.read()
        dummy_content=dummy_content.split(",")
        dummy_content=dummy_content[:-1]
        f_dummy.close()
        list_chunk=[]
        for ele in dummy_content:
            dummy_value=ele.split(":")[1]
            temp_chunk=ele.split(":")[0]
            if(int(dummy_value)==0):
                    list_chunk.append(temp_chunk)  
        k=0
        while(k<int(value)):
            query = gdata.docs.service.DocumentQuery(text_query=list_chunk[k])
            feed = self.gd_client.Query(query.ToUri())
            for entry in feed.entry:
                    if not feed.entry:
                        print 'No entries in feed.\n'
                        print '%-18s %-12s %s' % ('TITLE', 'TYPE', 'RESOURCE ID')
                    else:
                        temp = truncate(entry.title.text.encode('UTF-8'))
                        if temp == list_chunk[k]:
                            rid = entry.resourceId.text
                            filepath= list_chunk[k] + ".txt"
                            #print "filepath:" + filepath
                            newentry = self.client.GetDoc(rid)
                            self.client.Export(newentry, filepath)
                            title=list_chunk[k]
                            type = mimetypes.guess_type(filepath)
                            ms = gdata.MediaSource(file_path = filepath,content_type = type[0])
                            entry1 = self.gd_client.Upload(ms,title)
                            k = k+1"""
                    
        self.uploadmetadata()            
                             
            
    #Download parts of a file from Google docs and generate a single file.      
    def GDocDownload(self,filename):
        unique_filename=filename.split(".")[0]
        
        # Combines all the chunks of a file.
        def _combine(name,noc):
            f2 = open((unique_filename+".txt"),"wb")
            f2.close()
            for i in range(1,int(noc)+1):
                path_search = os.path.abspath((name+"_"+str(i)+"_base64.txt"))
                print "Currently open chunk:" + path_search
                f1= open(path_search,"rb")
                f2 =open(unique_filename+".txt","ab+")
                a = f1.read() 
                f1.close()
                #print "read file"
                b = base64.b64decode(a)
                #print "decoded file"
                f2.write(b)
                #print "file written"
            f2.close()
            
#chekcs if all necessary chunks are present
        def allchunks(initial_line,name):
                f_file=open("info.doc","r")
                cont = f_file.read()
                f_file.close()
                filename_temp =cont.split(":")[0]
                filename_temp=filename_temp.split(".")[0]
                noc=cont.split(":")[1]
                #print "filename:" + filename_temp
                #print "noc:" +str(noc)
                f_file=open("file_info.doc","r")
                content=f_file.read()
                f_file.close()
                content=content.split("\n")
                for item in content:
                    temp_file=item.split(":")[0].split(".")[0]
                    temp_code= item.split(":")[1]
                    if(temp_code==name):
                        filename=temp_file
                        print "filename:" + filename
            
                if(len(initial_line)==int(noc)):
                    _combine(name,noc)
                    
        # checks if missing chunk can be retrieved form the xored chunk.
        
        def _1xorsearch(filename,noc,miss_list,initial_line,file_list_1xor,file_list_2xor,counter_file):
            initial_line1=initial_line
            for k in range(len(miss_list)):
                for item in file_list_1xor:
                    name=item.split("_")[0]
                    temp_chunk1=item.split("x")[0].split("_")[1]
                    temp_chunk2=item.split("x")[1]
                    if(temp_chunk1==miss_list[k].split("_")[1]):
                        #print "first chunk is equal"
                        for j in range(len(initial_line)):
                            if(temp_chunk2==initial_line[j].split("_")[1]):
                                #print "got second chunk also"
                                f_file1=open((item+"_base64.txt"),"rb")
                                text=f_file1.read()
                                f_file1.close()
                                s = base64.b64decode(text)
                                f_file2=open((name+"_"+temp_chunk2+"_base64.txt"),"rb")
                                text2=f_file2.read()
                                f_file2.close()
                                u = base64.b64decode(text2)
                                f5=open((name+"_"+temp_chunk1+".txt"),"wb")
                                for i in range(len(s)):
                                        string12 = chr(ord(s[i])^ord(u[i]))
                                        f5.write(string12)
                                f5.close()
                                initial_line1.append((name+"_"+temp_chunk1))
                                temp_list=[]
                                for i in range(len(miss_list)):
                                    if(miss_list[i]!= temp_chunk1):
                                        temp_list.append(miss_list[i])
                                miss_list=temp_list
                                #print miss_list
                                f5=open((name+"_"+temp_chunk1+".txt"),"rb")
                                v=f5.read()
                                text3= base64.b64encode(v)
                                f6=open((name+"_"+temp_chunk1+"_base64.txt"),"wb")
                                f6.write(text3)
                                f6.close()
                    elif(temp_chunk2==miss_list[k].split("_")[1]):
                        #print "second chunk is equal"
                        for j in range(len(initial_line)):
                            if(temp_chunk1==initial_line[j].split("_")[1]):
                                #print "got first chunk also"
                                f_file1=open((item+"_base64.txt"),"rb")
                                text=f_file1.read()
                                f_file1.close()
                                s = base64.b64decode(text)
                                f_file2=open((name+"_"+temp_chunk1+"_base64.txt"),"rb")
                                text2=f_file2.read()
                                f_file2.close()
                                u = base64.b64decode(text2)
                                f5=open((name+"_"+temp_chunk2+".txt"),"wb")
                                for i in range(len(s)):
                                        string12 = chr(ord(s[i])^ord(u[i]))
                                        f5.write(string12)
                                f5.close()
                                initial_line1.append((name+"_"+temp_chunk2))
                                temp_list=[]
                                for i in range(len(miss_list)):
                                    if(miss_list[i]!= temp_chunk2):
                                        temp_list.append(miss_list[i])
                                miss_list=temp_list
                                #print miss_list
                                f5=open((name+"_"+temp_chunk2+".txt"),"rb")
                                v=f5.read()
                                text3= base64.b64encode(v)
                                f6=open((name+"_"+temp_chunk2+"_base64.txt"),"wb")
                                f6.write(text3)
                                f6.close()
                                
                        
            if(len(initial_line1)==int(noc)):
                allchunks(initial_line1,name) 
            else:
                #print "call 2xor search" 
                counter_file=counter_file+1
                #print "counter_file:" + str(counter_file)
            if (counter_file==2):
                tkMessageBox.showinfo("Message", "File Recovery is not possible")
                #print "file recovery is not possible"
                #sys.exit()
            else:
                _2xorsearch(filename,noc,miss_list,initial_line1,file_list_1xor,file_list_2xor,initial_line,counter_file)
                
        #If Missing chunk can be retrieved from another xored files. 
                
        def _2xorsearch(filename,noc,miss_list,initial_line1,file_list_1xor,file_list_2xor,initial_line,counter_file):
                initial_line2=initial_line1
                for k in range(len(miss_list)):
                    for item in file_list_2xor:
                        #print item
                        name=item.split("_")[0]
                        temp_chunk1=item.split("x")[0].split("_")[1]
                        temp_chunk2=item.split("x")[1]
                        if(temp_chunk1==miss_list[k].split("_")[1]):
                            print "first chunk is equal"
                            for j in range(len(initial_line)):
                                if(temp_chunk2==initial_line1[j].split("_")[1]):
                                    f_file1=open((item+"_base64.txt"),"rb")
                                    text=f_file1.read()
                                    f_file1.close()
                                    s = base64.b64decode(text)
                                    f_file2=open((name+"_"+temp_chunk2+"_base64.txt"),"rb")
                                    text2=f_file2.read()
                                    f_file2.close()
                                    u = base64.b64decode(text2)
                                    f5=open((name+"_"+temp_chunk1+".txt"),"wb")
                                    for i in range(len(s)):
                                            string12 = chr(ord(s[i])^ord(u[i]))
                                            f5.write(string12)
                                    f5.close()
                                    initial_line2.append((name+"_"+temp_chunk1))
                                    temp_list=[]
                                    for i in range(len(miss_list)):
                                        if(miss_list[i]!= temp_chunk1):
                                            temp_list.append(miss_list[i])
                                    miss_list=temp_list
                                    print miss_list
                                    f5=open((name+"_"+temp_chunk1+".txt"),"rb")
                                    v=f5.read()
                                    text3= base64.b64encode(v)
                                    f6=open((name+"_"+temp_chunk1+"_base64.txt"),"wb")
                                    f6.write(text3)
                                    f6.close()
                        elif(temp_chunk2==miss_list[k].split("_")[1]):
                            print "second chunk is equal"
                            for j in range(len(initial_line)):
                                if(temp_chunk1==initial_line1[j].split("_")[1]):
                                    print "got first chunk also"
                                    f_file1=open((item+"_base64.txt"),"rb")
                                    text=f_file1.read()
                                    f_file1.close()
                                    s = base64.b64decode(text)
                                    f_file2=open((name+"_"+temp_chunk1+"_base64.txt"),"rb")
                                    text2=f_file2.read()
                                    f_file2.close()
                                    u = base64.b64decode(text2)
                                    f5=open((name+"_"+temp_chunk2+".txt"),"wb")
                                    for i in range(len(s)):
                                            string12 = chr(ord(s[i])^ord(u[i]))
                                            f5.write(string12)
                                    f5.close()
                                    initial_line2.append((name+"_"+temp_chunk2))
                                    temp_list=[]
                                    for i in range(len(miss_list)):
                                        if(miss_list[i]!= temp_chunk2):
                                            temp_list.append(miss_list[i])
                                    miss_list=temp_list
                                    print miss_list
                                    f5=open((name+"_"+temp_chunk2+".txt"),"rb")
                                    v=f5.read()
                                    text3= base64.b64encode(v)
                                    f6=open((name+"_"+temp_chunk2+"_base64.txt"),"wb")
                                    f6.write(text3)
                                    f6.close()
                                    
                        if(len(initial_line2)==int(noc)):
                            allchunks(initial_line,name) 
                        elif(len(initial_line1) != len(initial_line2)):
                            counter_file= counter_file+1
                            print "counter_file:" + str(counter_file)
                            _1xorsearch(filename,noc,miss_list,initial_line,file_list_1xor,file_list_2xor)
        # download all metadata files
                
        # Decrypt all metadata files.
        def decryptmetadata(meta_file):
            f=open(meta_file,"r")
            content_meta=f.read()
            f.close()
            os.remove(meta_file)
            f=open(meta_file,"wb")
            f.write(base64.b64decode(content_meta))
            f.close()
            f=open(meta_file,"rb")
            content_meta=f.read()
            f.close()
            #print content_meta
            os.remove(meta_file)
            content_meta=content_meta.split("::::")[0]
            f=open(meta_file,"wb")
            f.write(content_meta)
            f.close()
                  
            f_meta=open("Metadata.txt","r")
            content_meta=f_meta.read()
            content_meta=content_meta.split(":")
            #print content_meta
            hash=content_meta[2]
            f_meta.close()
            
            f=open(meta_file,"rb")
            line_string=f.read()
            f.close()
            os.remove(meta_file)
            
            iv = '\0' * 32
            cipher = EVP.Cipher('aes_128_cbc', key=hash, iv=iv, op=0)
            fin = open(meta_file,"w")
            fin.write(cipher.update(line_string))
            fin.write(cipher.final())
            fin.close()
        
        for i in range(1,5):
            query = gdata.docs.service.DocumentQuery(text_query=str(i-1))
            feed = self.gd_client.Query(query.ToUri())
            for entry in feed.entry:
                if not feed.entry:
                    print 'No entries in feed.\n'
                    print '%-18s %-12s %s' % ('TITLE', 'TYPE', 'RESOURCE ID')
                else:
                    temp = truncate(entry.title.text.encode('UTF-8'))
                    if temp == str(i-1):
                        rid = entry.resourceId.text
                        if (temp==str(0)):
                            filepath="info_dummy.txt"
                        elif (temp==str(1)):
                            filepath="blockfile.txt"
                        elif(temp==str(2)):
                            filepath="file_info.txt"
                        elif(temp==str(3)):
                            filepath="info1.txt"
                        newentry = self.client.GetDoc(rid)
                        self.client.Export(newentry, filepath)
        
        decryptmetadata("info_dummy.txt")
        decryptmetadata("blockfile.txt")
        decryptmetadata("file_info.txt")
        decryptmetadata("info1.txt")
        filesearch_download(unique_filename)                
        counter_file= 0
        temp_newfile=open("blockfile.txt","r")
        cont=temp_newfile.read()
        cont= cont.split("\n")
        cont=cont[:-1]
        temp_newfile.close()
        temp_file=open("file_info.txt","r")
        content=temp_file.read()
        temp_file.close()
        content=content.split("\n")
        content = content[:-1]
        for item in content:
            temp_data=item.split(":")[1]
            temp_filename=item.split(":")[0]
            temp_filename=temp_filename.split(".")[0]
            if(filename==temp_filename):
                filename=temp_data
        list1=[]
        for item in cont:
            temp_chunk=item.split(":")[0]
            temp_newfile=temp_chunk.split("_")[0]
            temp_chunk=item.split(":")[1]
            if(filename==temp_newfile):
                    list1.append(temp_chunk)
        
        list2=[]
        for i in range(len(list1)):
            query = gdata.docs.service.DocumentQuery(text_query=list1[i])
            feed = self.gd_client.Query(query.ToUri())
            for entry in feed.entry:
                if not feed.entry:
                    print 'No entries in feed.\n'
                    print '%-18s %-12s %s' % ('TITLE', 'TYPE', 'RESOURCE ID')
                else:
                    temp = truncate(entry.title.text.encode('UTF-8'))
                    if temp == list1[i]:
                        rid = entry.resourceId.text
                        for item in cont:
                            temp_newfile=item.split(":")[0]
                            temp_chunk=item.split(":")[1]
                            if(temp==temp_chunk):
                                list2.append(temp_newfile)
                                filepath= temp_newfile+"_base64.txt"
                                newentry = self.client.GetDoc(rid)
                                self.client.Export(newentry, filepath)

        print "document downloaded"
        initial_line_old=[]
        file_list_1xor=[]
        file_list_2xor=[]
        list_temp=[]
        list_valid=[]
        for i in range(len(list2)):
            if(list2[i].count("c")!=0):
                list_temp.append(list2[i])
            else:
                list_valid.append(list2[i])
        for i in range(len(list_valid)):
            if(list_valid[i].count("x")==0):
                initial_line_old.append(list_valid[i])
            else:
                newchunk1=list_valid[i].split("x")[1]
                newchunk2=list_valid[i].split("x")[0].split("_")[1]
                if(int(newchunk1)==int(newchunk2)+1):
                    file_list_1xor.append(list_valid[i])
                elif(int(newchunk1)==int(newchunk2)+2):
                    file_list_2xor.append(list_valid[i])
            
        if(len(list_temp)!=0):
            for i in range(len(list_temp)):
                file_list_2xor.append(list_temp[i])
        f=open("info1.txt","r")
        content=f.read()
        content=content.split("\n\n\n\n")
        f.close()
        for item in content:
            temp_filename= item.split(":")[0]
            if(temp_filename==filename):
                noc=str(item.split(":")[1].split("::::::")[0])
        initial_line=[]
        miss_list=[]
        print "Chunks to be recovered are:" + str(noc)
        for i in range(1,int(noc)+1):
            path_search = os.path.abspath((filename+ "_"+str(i)+"_base64.txt")) 
            #print "path search:" + str(path_search)
            if(os.path.exists(path_search)):
                initial_line.append((filename+"_"+str(i)))
            else:
                miss_list.append((filename+"_"+str(i))) 
        if(len(miss_list)==0):
                #print "Got all the chunks call combine to form file"
                _combine(filename,noc)
        else:
                #print "Chunks are missing recover them"
                _1xorsearch(filename,noc,miss_list,initial_line,file_list_1xor,file_list_2xor,counter_file)
        filesearch_download(unique_filename)
        fo = open("info1.txt","rb")
        z =filename
        for line in fo:
            if not line.strip():
                continue
            else:
                y = line.split(':')[0]
                #print "Y",y
                if (y == z):
                    w = line.split('::::::')[1]
                    key1 = line.split('::::::')[2]
                    key1=base64.b64decode(key1)
                    ab = w.split(',')
                    break
        
        #Additional number of download
        
        """f_file=open("file_info.txt","r")
        file_content=f_file.read()
        file_content=file_content.split("\n")
        file_content=file_content[:-1]
        f_file.close()
        #print filename
        #print file_content
        list_additional=[]
        for ele in file_content:
            temp_ele=ele.split(":")[1]
            print "temp_ele" + temp_ele
            print "filename"+ filename
            if(temp_ele==filename):
                temp_chunk_add=ele.split(":")[2]
        temp_chunk_add=int(temp_chunk_add)
        print "temp_chunk_add"
        print temp_chunk_add
        f_dummy=open("info_dummy.txt","r")
        dummy_content= f_dummy.read()
        dummy_content=dummy_content.split(",")
        dummy_content=dummy_content[:-1]
        f_dummy.close()
        list_chunk=[]
        for ele in dummy_content:
            dummy_value=ele.split(":")[1]
            temp_chunk=ele.split(":")[0]
            if(int(dummy_value)==0):
                    list_chunk.append(temp_chunk)   
        print list_chunk
        k=0
        while(k<temp_chunk_add):
            query = gdata.docs.service.DocumentQuery(text_query=list_chunk[k])
            feed = self.gd_client.Query(query.ToUri())
            for entry in feed.entry:
                    if not feed.entry:
                        print 'No entries in feed.\n'
                        print '%-18s %-12s %s' % ('TITLE', 'TYPE', 'RESOURCE ID')
                    else:
                        temp = truncate(entry.title.text.encode('UTF-8'))
                        if temp == list_chunk[k]:
                            rid = entry.resourceId.text
                            filepath= list_chunk[k] + ".txt"
                            print "filepath:" + filepath
                            newentry = self.client.GetDoc(rid)
                            self.client.Export(newentry, filepath)
                            k = k+1"""
                            
        #Decrypt a file
        print("Decrypting file...")
        f = open(unique_filename+".txt","rb")
        buffer = f.read()
        f.close()
        os.remove((unique_filename+".txt"))
        buffer=buffer.split("::::")[0]
        iv = '\0' * 32
        cipher = EVP.Cipher('aes_128_cbc', key=key1, iv=iv, op=0)
        outfile = 'decrypted' + '_' + unique_filename+".txt"
        f1 = open(outfile,"w")    
        f1.write(cipher.update(buffer))
        f1.write(cipher.final())
        f.close()
        f1.close()
        final_name = outfile.split('.')[0]
        final_name = final_name + '.' + 'doc'
        fin1 = open(outfile,"rb")
        fin2 = open(final_name,"wb")
        we = fin1.read()
        fin2.write(we)
        fin1.close()
        fin2.close()
        print("File is ready !!!")
        
   
    # Format Google docs with random dummy files.    
    def _FormatDocuments(self,storage):
        num = int(storage)
        f = open("info_dummy.txt","w")
        for i in range(4,num+4):
            file_name = str(i) + '.' + 'txt'
            f.write(str(i) + ":" + "0" + ",")
            file_path = os.path.realpath(file_name)
            title = file_path.split('/')[-1]
            title = title.split('.')[0]
            type = mimetypes.guess_type(file_path)
            ms = gdata.MediaSource(file_path = file_path,content_type = type[0])
            entry = self.gd_client.Upload(ms,title)
        f.close()
    
    # List of all documents present in Google docs.    
    def _ListAllDocuments(self):

        temp_file=open("file_info.doc","r")
        content=temp_file.read()
        temp_file.close()
        content=content.split("\n")
        #print "Files uploaded to google docs are:"
        for item in content:
            temp_data=item.split(":")[1]
            temp_filename=item.split(":")[0]
            print temp_filename
    def encrypt_metadata(self,hash,meta_file):
        f=open(meta_file,"r")
        buffer = f.read()
        f.close()
        #os.remove(meta_file)
        iv = '\0' * 32
        cipher = EVP.Cipher('aes_128_cbc', key=hash, iv=iv, op=1)
        fin = open(meta_file.split(".")[0] + ".txt","wb")
        fin.write(cipher.update(buffer))
        fin.write(cipher.final())
        fin.close()
        size_meta=os.path.getsize(meta_file)
        #print "size after encrypting" + str(size_meta)
        additional_size=256000 -size_meta
        f=open(meta_file.split(".")[0] + ".txt","ab")
        f.write("::::")
        for i in range(1,additional_size/2+1-2):
                f.write('&&')
        f.close()
        #print "size after adding bytes" + str(os.path.getsize(meta_file))
        f=open(meta_file.split(".")[0] + ".txt","rb")
        content_meta=f.read()
        f.close()
        #os.remove(meta_file)
        f=open(meta_file.split(".")[0] + ".txt","w")
        f.write(base64.b64encode(content_meta))
        f.close()
        #print "size after base64 encoding:" + str(os.path.getsize(meta_file))
        
    def uploadmetadata(self):
        f_meta=open("Metadata.txt","r")
        content_meta=f_meta.read()
        content_meta=content_meta.split(":")
        #print content_meta
        hash=content_meta[2]
        f_meta.close()
        # upload all metadata files.
        meta_file="info_dummy.txt"
        self.encrypt_metadata(hash,meta_file)    
        file_path = os.path.realpath(meta_file.split(".")[0] + ".txt")
        #print "size of final file:" + str(os.path.getsize(meta_file))
        type = mimetypes.guess_type(file_path)
        title = str(0)
        type = mimetypes.guess_type(file_path)
        ms = gdata.MediaSource(file_path = file_path,content_type = type[0])
        entry1 = self.gd_client.Upload(ms,title)
        
        meta_file="blockfile.txt"
        self.encrypt_metadata(hash,meta_file)    
        file_path = os.path.realpath(meta_file.split(".")[0] + ".txt")
        type = mimetypes.guess_type(file_path)
        title = str(1)
        type = mimetypes.guess_type(file_path)
        ms = gdata.MediaSource(file_path = file_path,content_type = type[0])
        entry1 = self.gd_client.Upload(ms,title)

        
        
        
        meta_file="file_info.txt"
        self.encrypt_metadata(hash,meta_file)    
        file_path = os.path.realpath(meta_file.split(".")[0] + ".txt")
        type = mimetypes.guess_type(file_path)
        title = str(2)
        type = mimetypes.guess_type(file_path)
        ms = gdata.MediaSource(file_path = file_path,content_type = type[0])
        entry1 = self.gd_client.Upload(ms,title)
        
        meta_file="info1.txt"
        self.encrypt_metadata(hash,meta_file)    
        file_path = os.path.realpath(meta_file.split(".")[0] + ".txt")
        type = mimetypes.guess_type(file_path)
        title = str(3)
        type = mimetypes.guess_type(file_path)
        ms = gdata.MediaSource(file_path = file_path,content_type = type[0])
        entry1 = self.gd_client.Upload(ms,title)
                  
        
     
    def metadatasecurity(self):
        secure_password=raw_input("Enter password:")
        if(os.path.exists("Metadata.txt")):
            f_meta=open("Metadata.txt","r")
            content_meta=f_meta.read()
            content_meta=content_meta.split(":")
            #print content_meta
            hash=content_meta[2]
            f_meta.close()
            if(pbkdf2_sha512.verify(secure_password,hash)):
                print " Authentication successful!!" 
            else:
                print "Authetication failed!!"
                sys.exit()
                  
        else:
            #print "create metadata file"
            salt_initial=""
            for i in range(1,11):
                salt_initial +=chr(random.randint(1,256))
            salt=base64.b64encode(salt_initial)
            hash = pbkdf2_sha512.encrypt(secure_password, rounds=8000, salt=salt)
            print  hash  
            s = hash.split("$")
            key_encrypt=s[4]
            f_meta=open("Metadata.txt","w")
            f_meta.write(s[2]+":"+s[3]+":"+hash)
            f_meta.close()
            



class MyApp:
    username=""
    password=""
    password2=""
    def __init__(self, parent):
        self.myParent = parent   
        mc1 = self.myContainer1 = Frame(parent,bg="light blue", relief=SUNKEN)
        
        self.myContainer1.pack()
        var = IntVar()

        self.LabelUN = Label(self.myContainer1, text="UserName:",bg="light blue",fg="blue")
        self.LabelUN.grid(row=0, sticky=W)
        #self.LabelUN.pack(side=LEFT,padx=5,pady=5)
        self.entryUN = Entry(self.myContainer1, width=20)
        self.entryUN.grid(row=0, column=1)
        #self.entryUN.pack(side=LEFT,padx=5,pady=5)
        
        self.LabelPWD = Label(self.myContainer1, text="Password:",bg="light blue",fg="blue")
        self.LabelPWD.grid(row=1,sticky=W)
        #self.LabelPWD.pack(side=LEFT, padx=5, pady=5)
        self.entryPWD = Entry(self.myContainer1, width=20,show="*")
        self.entryPWD.grid(row=1, column=1)
        #self.entryPWD.pack(side=LEFT,padx=5,pady=5)

        self.button1 = Button(self.myContainer1,bg="green", command=self.setcredentials)  
        self.button1.configure(text="Login")
        self.button1.grid(row=2, column=1,sticky=W)
        #self.button1.pack(side=LEFT)
        self.button1.focus_force()       
        
        self.button2 = Button(self.myContainer1, bg="green",command=self.button2Click)   
        self.button2.configure(text="Cancel")       
        self.button2.grid(row=2, column=1,sticky=E)
        #self.button2.pack(side=LEFT)
    
    def setcredentials(self):
        self.username = self.entryUN.get()
        self.password = self.entryPWD.get()
        
        try:
            #service = gdata.apps.service.AppsService(email=self.username, password=self.password)
            sample = DocsSample(self.username,self.password)
            #print "I just logged in successfully!"
            myapp.destroyMyself()
                    #print "username:",username                
        except:
            
            tkMessageBox.showinfo("Invalid credetials ",'Invalid user credentials given.')
            #myapp.__init__(root)
        
    def destroyMyself(self):    
        self.myParent.destroy()
        
    def getcredentials(self):
        return self.username,self.password
    
    def button2Click(self): ### (2)
        #print "button2Click event handler"
        username = self.entryUN.get()
        password = self.entryPWD.get()
        self.entryUN.delete(0,len(username))
        self.entryPWD.delete(0,len(password))
        #self.myParent.destroy()    
class MyApp1:
        pwd2 = ""
        optiontype = ""
        storage = ""
        filepath = ""
        def __init__(self, parent):
                self.myParent = parent   
                mc1 = self.myContainer1 = Frame(parent,bg="light blue", relief=SUNKEN)

                self.myContainer1.pack()
                self.var1 = StringVar()
                
                self.LabelPWD2 = Label(self.myContainer1, text="Password:",bg="light blue",fg="blue")
                self.LabelPWD2.grid(row=0,column=1)
                #self.LabelPWD2.pack(side=LEFT, padx=5, pady=5)
                self.entryPWD2 = Entry(self.myContainer1, width=10,show="*")
                self.entryPWD2.grid(row=0, column=2)
                #self.entryPWD2.pack(side=LEFT,padx=5,pady=5)

                
                R1 = Radiobutton(self.myContainer1, text="List", variable=self.var1, value="List",bg="light blue",fg="blue")
                #R1.pack( anchor = W )
                R1.grid(row=1, column=1)
                R2 = Radiobutton(self.myContainer1, text="Format", variable=self.var1, value="Format",bg="light blue",fg="blue")
                #R2.pack( anchor = W )
                R1.grid(row=1, column=2)
                
                R3 = Radiobutton(self.myContainer1, text="Upload", variable=self.var1, value="Upload",bg="light blue",fg="blue")
                #R3.pack( anchor = W)
                R1.grid(row=2, column=1)
                R4 = Radiobutton(self.myContainer1, text="Download", variable=self.var1, value="Download",bg="light blue",fg="blue")
                #R4.pack( anchor = W)
                R1.grid(row=2, column=2)
                
                self.LabelPWD = Label(self.myContainer1, text="Filename:",bg="light blue",fg="blue")
                #self.LabelPWD.pack(side=TOP, padx=5, pady=5)
                self.LabelPWD.grid(row=3, column=1)
                self.entryFile = Entry(self.myContainer1, width=10)
                #self.entryFile.pack(side=TOP,padx=10,pady=10)
                self.entryFile.grid(row=3, column=2)
                
                self.button2 = Button(self.myContainer1, bg="green", command=self.browseClick)
                self.button2.configure(text="Browse")
                #self.button2.pack(side=TOP)
                self.button2.grid(row=3, column=3)

                
                self.LabelStore = Label(self.myContainer1, text="Storage:",bg="light blue",fg="blue")
                #self.LabelStore.pack(side=TOP,padx=10,pady=10)
                self.LabelStore.grid(row=4, column=1)
                self.entryStore = Entry(self.myContainer1, width=10)
                #self.entryStore.pack(side=TOP,padx=10,pady=10)
                self.entryStore.grid(row=4, column=2)

                self.button1 = Button(self.myContainer1,bg="green",  command=self.setOptionTypes)  
                self.button1.configure(text="Submit")
                #self.button1.pack(side=TOP)
                self.button1.grid(row=5, column=1)
                self.button1.focus_force()

                                
                self.button3 = Button(self.myContainer1, bg="green", command=self.exitWindow)
                self.button3.configure(text="Exit")
                #self.button3.pack(side=TOP)
                self.button3.grid(row=5, column=2)
                
        def setOptionTypes(self):  ### (2)
                #print "button1Click event handler"
                self.pwd2 = self.entryPWD2.get()
                self.storage = self.entryStore.get()
                self.filepath = self.entryFile.get()
                self.optiontype = self.var1.get()
        
                # Check passwod here first
                if(os.path.exists("Metadata.txt")):
                        print "file found"
                        f_meta=open("Metadata.txt","r")
                        content_meta=f_meta.read()
                        content_meta=content_meta.split(":")
                        #print content_meta
                        hash=content_meta[2]
                        f_meta.close()
                        if(pbkdf2_sha512.verify(self.pwd2,hash)):
                            print " Authentication successful!!" 
                        else:
                            print "Authetication failed!!"
                            sys.exit()
                              
                else:
                        print "create metadata file"
                        salt_initial=""
                        for i in range(1,11):
                            salt_initial +=chr(random.randint(1,256))
                        salt=base64.b64encode(salt_initial)
                        hash = pbkdf2_sha512.encrypt(self.pwd2, rounds=8000, salt=salt)
                        print  hash  
                        s = hash.split("$")
                        key_encrypt=s[4]
                        f_meta=open("Metadata.txt","w")
                        f_meta.write(s[2]+":"+s[3]+":"+hash)
                        f_meta.close()
            
                    #self.metadatasecurity()
                    #self._PrintMenu()
                    #choice = self._GetMenuChoice(7)
                if self.optiontype == "List":
                            sample._ListAllDocuments()
                elif self.optiontype == "Format":
                            print "2"
                            #print type(self.storage)
                            sample._FormatDocuments(self.storage)
                elif self.optiontype == "Upload":
                            print "3"
                            sample._UploadMenu(self.filepath)
                elif self.optiontype == "Download":
                            print "4"
                            sample.GDocDownload(self.filepath)
                elif choice == 5:
                            return
                        
                self.clearData()
                    
                
        def clearData(self): ### (2)
                #print "button2Click event handler"
                self.storage = self.entryStore.get()
                self.pwd2 = self.entryPWD2.get()
                self.filepath = self.entryFile.get()
                self.entryStore.delete(0,len(self.storage))
                self.entryPWD2.delete(0,len(self.pwd2))
                self.entryFile.delete(0,len(self.filepath))
                
        def exitWindow(self):        
                self.myParent.destroy()

        def browseClick(self):
                filename = askopenfilename(filetypes=[("Doc files","*.doc")])
                tmp = filename.replace("/","\\")
                print "File:",tmp
                self.entryFile.delete(0,len(self.entryFile.get()))
                self.entryFile.config(width=len(tmp)+5)
                self.entryFile.insert(0,tmp)
                            
root = Tk()
root.title("Login Form")
print "Madhvi"
myapp = MyApp(root)
root.mainloop()
print "I"
uname,pword = myapp.getcredentials()
print "you"
print "username: ",uname 
print "password: ",pword
sample=DocsSample(uname,pword)

"""except gdata.service.CaptchaRequired:
                    captcha_token = service._GetCaptchaToken()
                    url = service._GetCaptchaURL()
                    print "Please go to this URL:"
                    print "  " 
                    print url
                    captcha_response = raw_input("Type the captcha image here: ")
                    service.ProgrammaticLogin(captcha_token, captcha_response)
                    print "Done!"""

                
        
root1 = Tk()
root1.title("Menu Form")
myapp1 = MyApp1(root1)
root1.mainloop()

#sample=DocsSample(myapp.button1Click)

