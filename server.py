# server.py
import socket
import threading
import random
import hashlib


file = open("small_file.txt","r")
lines = file.readlines()
num_lines = len(lines)
file_str =""
for i in range(len(lines)):
    lines[i]= str(i+1)+"\n"+lines[i]
    if(i == len(lines)):
        lines[i]+="\n"
    file_str+=lines[i]
file.close()
file_str_md5 = hashlib.md5(file_str.encode())


client_list = []
max_client = 20
connection_thread = []
# to be changed --server ip
server_ip = "192.168.163.135"

def start_server():
    global server_ip
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((server_ip,9806))
    return server

def send_data(cnskt):
    global num_lines
    # index = 0
    while(True):
        msg = cnskt.recv(1024*16*num_lines).decode()
        if(msg=="SENDLINE\n"):
            # index+=1
            # if(index==10):
                # cnskt.send(b"-1\n\n")
                # index=0
                # continue
            line_num = random.randint(0,num_lines-1)
            cnskt.send(lines[line_num].encode())
        elif (msg[:7]=="SUBMIT\n"):
            msg = msg[7:]
            result_hash = hashlib.md5(msg.encode())
            print(f"\nReceived hash: {result_hash.hexdigest()}")  # Print the received hash
            print(f"Expected hash: {file_str_md5.hexdigest()}")  # Print the expected (given) hash
            if(result_hash.hexdigest() == file_str_md5.hexdigest()):
                cnskt.send(b"\nSuccess...\nFiles matched.\n")
            else:
                cnskt.send(b"\nFailed...\nFiles doesnot matched.\n")
            print("\nConnection ended with client:", cnskt.getpeername())  # Show connection end message
            cnskt.close()
            break        


def connect(skt):
    global client_list
    while(True):
        cs,address = skt.accept()
        client_list.append((cs,address))
        print("\nConnected with client:",address)
        connection_thread.append(threading.Thread(target=send_data,args=[cs]))
        connection_thread[-1].start()


server_skt = start_server()
server_skt.listen(max_client)
print("\nServer started....")
connect(server_skt)
