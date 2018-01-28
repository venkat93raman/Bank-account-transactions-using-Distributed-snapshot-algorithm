import time
import os
import random
from socket import *
from thread import *
import threading
theDict={}
names={}
my_pid=0
client_counter=1
conn_counter=0
reply_counter=0
polled = False
my_port=0
my_host='localhost'
my_name=''
Queue=[]
saved_money=0
my_money=1000
lamport_clock=0
#flag=[]
receive_counter={}
channel={}
flag={}
saved_money={}

def config():
    global my_pid
    global my_port
    global client_counter
    global my_name
    print "Configuration phase "
    my_pid=os.getpid()
    #print 'My pid = ',my_pid
    my_name=raw_input('Enter your Name : ')
    f=open("config","a+")
    line=''
    ip=''
    port=''
    for line in f:
        ip,port,name=line.strip().split(' ')
        #print ip,port
        client_counter=client_counter+1
    f.close()

    f=open("config","a")
    if line:
        port=str(int(port)+1000)
    else:
        port=str(random.randint(3000,9999))
    my_port=int(port)
    #print 'my port = ',my_port
    f.write('127.0.0.1 '+port+' '+my_name+'\n')
    f.close()
    return (ip,port)

def read_config():
    #print "read config"
    f=open("config","r")
    global client_counter
    client_counter=0
    line=''
    ip=''
    port=''
    for line in f:
        ip,port,name=line.strip().split(' ')
        #print ip,port,name
        client_counter=client_counter+1
    f.close()
    return (ip,port,name)

def fetch_line(line_num):
    f=open("config","r")
    count=0
    for line in f:
        ip,port,name=line.strip().split(' ')
        count=count+1
        if (count == int(line_num)):
            break
    return (ip,port,name)

    
def poll():
    print "Polling Phase"
    global polled
    temp_counter=client_counter
    read_config()
    if temp_counter<client_counter:
        count=client_counter-temp_counter
        for i in range(count):
            ip,port,name= fetch_line(i+1+temp_counter)
            polled = True
            #print ip,port,name,"poll "
            tcp_connect(ip,port)
    return
            
def tcp_wait():
    sock = socket(AF_INET,SOCK_STREAM)
    sock.bind((my_host,my_port))
    sock.listen(5)
    global conn_counter
    global theDict
    while True:
        conn, addr = sock.accept()
        #print theDict
        #print conn,addr
        t=threading.Thread(target=clientthread,args=(conn, conn_counter))
        t.start()
        if (conn):
            conn_counter=conn_counter+1
            break
    return


def clientthread(conn,conn_counter):
    global theDict
    
    conn.send('I am '+my_name)
    data=conn.recv(1024)
    #print data
    data=data.strip().split('I am ')
    theDict[conn_counter]=conn
    names[conn_counter]=data[1]
    return
    

	



def tcp_connect(ip,port):
    #print ip,port
    global theDict
    global conn_counter
    sock=socket(AF_INET,SOCK_STREAM)
    sock.connect((ip,int(port)))
    
    data=sock.recv(1024)
    #print data
    data=data.strip().split('I am ')
    theDict[conn_counter]=sock
    names[conn_counter]=data[1]
    conn_counter=conn_counter+1
    sock.send('I am '+my_name)
    return

def tcp_send(msg,socket_num):
    #print "thread send"
    #t=threading.Thread(target=send_msg,args=(msg,socket_num))
    #t.start()
    #t.sleep(3)
    if socket_num=='all':
        for i in range(conn_counter):
            theDict[i].send(msg)
    else:
            theDict[socket_num].send(msg)
    return


def send_msg(msg,socket_num):
    #print "actual send"
    if socket_num=='all':
        for i in range(conn_counter):
            theDict[i].send(msg)
        else:
            theDict[socket_num].send(msg)
    return



def tcp_recv(temp):
    
    #print "----------------------------------receiving"
    global my_money
    global flag
    global receive_counter
    global channel
    global saved_money
    while True:
        try:
            for i in range(conn_counter):
                try:
                    #print receive_counter
                    theDict[i].settimeout(0)
                    data=theDict[i].recv(300)
                    msg=data.strip()
##                    if(msg.isdigit()):
##                        print "rceived money = ",int(msg)
                    if("marker" in msg):
                        #print msg
                        temp=msg.split('marker')
                        temp=temp[1]
                        if(flag[temp]!=1):
                            print "Received marker from "+ str(names[i])+"\n"
                            saved_money[temp]=my_money
                            flag[temp]=1
                            receive_counter[temp]=receive_counter[temp]+1
                            #print receive_counter
                            u=threading.Timer(3,tcp_send,args=(('marker'+str(temp)),'all'))
                            u.start()
                        elif(flag[temp]==1):
                            print "Received marker from "+ str(names[i])+"\n"
                            if(receive_counter[temp]!=conn_counter):
                                receive_counter[temp]=receive_counter[temp]+1
                            if(receive_counter[temp]==conn_counter):
                                receive_counter[temp]=0
                                flag[temp]=0
                                print "Saved State(Money) = ",saved_money[temp]
                                saved_money[temp]=0
                                print "Saved Channel States = ",channel[temp],"\n"
                                channel[temp]=[]
                    else:
                        
                        my_money=my_money+int(msg)
                        print 'Received '+msg+'$'+' from '+str(names[i])
                        print 'My money = ',my_money,"\n"
                        if(flag[my_name]==1):
                            print "Going to queue\n"
                            channel[my_name].append('Received '+msg+'$'+' from '+str(names[i]))
                           
    
                        for i in range (conn_counter):
                            if(flag[names[i]]==1):
                                print "Going to queue\n"
                                channel[names[i]].append('Received '+msg+'$'+' from '+str(names[i]))
                                
                        
                except:
                    #print 'no data from '+str(theDict[i])
                    pass
                
        except:
            print "thread error"
            pass


def get_client_counter():
    f=open("config","r")
    count=0
    for line in f:
        count=count+1
    return count




def start_new(temp):
    global my_money
    global receive_counter

    while True:
        #try:
            for i in range (conn_counter):
                time.sleep(1+random.random()*3)
                if(random.random()<0.2):
                    m=random.randrange(10,20)
                    my_money=my_money-m
                    print 'Sending '+str(m)+'$'+' to '+str(names[i])
                    print 'My money =',my_money,'\n'
                    #tcp_send(str(m),i)
                    t=threading.Timer(3,tcp_send,args=(str(m),i))
                    t.start()
                    #print threading.enumerate()
        #except:
            #print "start error"





#MAIN CODE




config()
while True:
    if (client_counter==1):
        poll()
        time.sleep(5)
    elif polled:
        #print "polling done"
        break
    else:
        #print "waiting"
        #raw_input()
        #wait for tcp connection
        tcp_wait()
        if conn_counter==client_counter-1:
            break
while True:
    poll()
    time.sleep(5+random.random()*3)
    #print theDict
    if conn_counter==2:
        break
f=open("config","w")
f.close()

channel[my_name]=[]
for i in range(conn_counter):
    channel[names[i]]=[]

flag[my_name]=0
for i in range(conn_counter):
    flag[names[i]]=0

saved_money[my_name]=0
for i in range(conn_counter):
    saved_money[names[i]]=0


receive_counter[my_name]=0
for i in range(conn_counter):
    receive_counter[names[i]]=0
##print "------------------------------------"
##
##print channel
##print flag
##print receive_counter
##print "------------------------------------"
start_new_thread(start_new,(1,))
start_new_thread(tcp_recv,(1,))

#print threading.enumerate()
#print "this is the post"
while True:
    receive_counter[my_name]=0
    print('Wanna take a snapshot ? (Y/N)\n')
    response=raw_input()
    if(response=='Y'or response=='y'):
        t=threading.Timer(3,tcp_send,args=('marker'+my_name,'all'))
        t.start()
        #tcp_send('marker','all')
        flag[my_name]=1
        saved_money[my_name]=my_money
        while(flag[my_name]==1):
            pass
        time.sleep(3)
    #flag=0
    #print Queue
    #Queue=[]
    









print "clients = "+str(client_counter)
