#client.py

import socket
import time
import threading

lock = threading.Lock()
lines_with_number={}
lines_get = 0
total_clients=0
total_lines=0
# lnr=-1
# lnr_is_updated=False
# completed=False
lstofdict=[]

def get_line_with_number(s):
    #  first take the line number :
    temp=""
    line_num=0
    line=""
    char=s.recv(1).decode()

    while(char!='\n'):
        temp+=char
        char=s.recv(1).decode()
    
    line_num=int(temp)

    char=""
    while(char!='\n'):
        line+=char
        char=s.recv(1).decode()
    return (line_num,line)



def recv_from_clients(s,addr_port,index):
    global lock
    global lstofdict
    global lines_get
    global total_lines
    buffersize = 400
    # print("Client is ready to receive from this client!!")
    while True:
      try:
         s.connect(addr_port)
         break
      except:
          continue
    
    # print("Connection suceeded: ", addr_port)
    while True:
        if (len(lines_with_number)==total_lines):
            break
        if lines_get>=total_lines:
            # s.close()
            break
        try:
            (no,line)=get_line_with_number(s)
        except:
            a=10

        if no not in lstofdict[index].keys():
            lstofdict[index][no]=line
            # print("RECV: ", len(lstofdict[index]))

        if(len(lstofdict[index]) == buffersize):
            
            with lock:
               
                # print("Updating LNR")
                for no in lstofdict[index]:
                    if no not in lines_with_number.keys():
                        lines_with_number[no]=lstofdict[index][no]
                        # print("lines updates by recv: ",len(lines_with_number))
                    if len(lines_with_number)==total_lines:
                        # print("lines updates by recv: ",len(lines_with_number))
                        # s.close()
                        break
                lines_get = len(lines_with_number)

            lstofdict[index].clear()

def get_data_from_main_server(s,list_of_clsockets):
    c = 0

    st = time.time()

    global lock
    global lines_with_number
    global total_lines
    # s.connect(('socket.gethostbyname('')',9801))
    
    # to be change  --- server ip
    s.connect(('192.168.163.135',9806))

    while True:
        sts="SENDLINE\n"
        s.sendall(sts.encode())

        temp=get_line_with_number(s)
        print(len(lines_with_number))

        if temp[0]==-1:
            print("-1 recieved")
            continue
        with lock:
            if len(lines_with_number)==total_lines and c == 0:
                sub = "SUBMIT\n"
                lines_with_number = dict(sorted(lines_with_number.items()))
                final_string =""
                for item in lines_with_number:
                    final_string += str(item)+"\n" + lines_with_number[item]+"\n"
                sub+=final_string
                s.send(sub.encode())
                print(s.recv(4096).decode())
                mt = time.time()
                c=1
                print("Total time taken is : ",mt-st)
                s.close()
                break

            if temp[0] not in lines_with_number.keys():
                lines_with_number[temp[0]]=temp[1]
                
        for i in range(len(list_of_clsockets)):
            send_data_to_client(list_of_clsockets[i][0],list_of_clsockets[i][1],i,temp)

          
def start_own_server():
    # to be changed --- self device ip
    device_ip="192.168.163.135"
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((device_ip,9802))
    return server


def send_data_to_client(s,addr,index,data):
    # print("Sending data to the client with address ",addr," ...")
    try:
        s.sendall((str(data[0])+"\n"+data[1]+"\n").encode())
        # s.sendall((data[1]+"\n").encode())
    except:
        # print("Client disconnected: ", addr)
        a = 10



def connect_to_other_clients(s,total_clients):
    s.listen(total_clients)
    print("Listening for the clients.....")
    l=[]
    for i in range(0,total_clients):
        cl,addr=s.accept()
        print("Client with ip address ",addr," is connected!!")
        l.append((cl,addr))
    return l


def entry_point():
    global total_clients
    global total_lines
    
    config_file=open("config.txt")
    lines=config_file.readlines()
    l=[]
    total_clients=int(lines[0])
    
    for i in  range(1,len(lines)-1):
        temp=lines[i].split(' ')
        l.append((temp[0],int(temp[1])))
    

    total_lines=int(lines[len(lines)-1])
    
    print("Total_clients are :: ",total_clients)
    print("List of addresses ",l)
    print("Total lines are : ",total_lines)               
    config_file.close()

    #   connection to main server
    socket_main_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    #  start own server
    client_server=start_own_server()

    #receiving from other clients:
    # l=[]   list of tuples containing the address of the servers and their ports
    # l=[('10.194.34.193',9802),('10.194.16.10',9802),('10.194.10.165',9802)]

    l2=[]
    for i in range(0,total_clients):
        temp=socket.socket()
        l2.append(temp)
    
    for i in range(0,total_clients):
        lstofdict.append({})
        threading.Thread(target=recv_from_clients,args=[l2[i],(l[i][0],l[i][1]),i]).start()

    list_of_clsockets=connect_to_other_clients(client_server,total_clients)
    temp=threading.Thread(target=get_data_from_main_server,args=[socket_main_server,list_of_clsockets])
    temp.start()

entry_point()
