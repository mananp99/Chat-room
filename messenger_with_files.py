# Manan Patel
# CSC 376
# Assignment 4: Messenger with File Transfer

import sys
import socket
import threading
import os
import getopt

## Handle messages being recieved - used in new thread
def msg_recv(sock):
    while True:
        try:
            msg = sock.recv(1024)
        except:
            break

        if len(msg.decode()) > 0:
            print(msg.decode())
        else:
            os._exit(0)
            break

## Handle sending messages
def msg_send(sock):
    while True:
        try:
            sock.send(input().encode())
        except EOFError:
            break

## Handle file transfer
def handle_file_req(sock):
    while True:
        try:
            fl_sock, addr = sock.accept()
            file = fl_sock.recv(1024).decode()
            print(file)
            file_stat = os.stat(file)
            if(file_stat.st_size):
                r_file = open(file,'rb')
                while True:
                    file_bytes = r_file.read(1024)
                    if(file_bytes):
                        fl_sock.send(file_bytes)
                    else:
                        break
                r_file.close()
            else:
                pass
            fl_sock.close()
        except OSError:
            pass

def file_recv(host,port,fname):
    fl_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if host:
        fl_sock.connect((host, int(port)))
    else:
        fl_sock.connect(('localhost',int(port)))
    try:
        fl_sock.send(fname.encode())
    except:
        sys.exit()
    w_file = open(fname,'wb')   
    while True:
        try:
            file_bytes = fl_sock.recv(1024)  
        except:
            break
        if len(file_bytes):
            w_file.write(file_bytes)
        else:
            fl_sock.close()
            break
    w_file.close()


def main():
    argc = len (sys.argv)
    if (argc < 3 or argc > 7):
        print('invalid number of arguments')
        sys.exit()

    is_server = False
    lstn_port = None
    conn_port = None
    server_addr = None

    opts,args = getopt.getopt(sys.argv[1:], "l:s:p:")
    for opt, arg in opts:
        if opt == '-l':
            lstn_port = arg
        if opt == '-p':
            conn_port = arg
        if opt == '-s':
            server_addr = arg
    
    if lstn_port is None:
        print("Listening port required")
        sys.exit()
    
    first_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)       # Server: First sock on port 6001
    first_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    first_sock.bind(('',int(lstn_port)))
    first_sock.listen(5)

    if(not conn_port):
        is_server = True

    if(is_server == True):

        sock,addr = first_sock.accept()
        server_addr = addr[0]
        
        recv_msg = sock.recv(1024)

        if(len(recv_msg)):
            msg = recv_msg.decode()
            conn_port = msg
        else:
            sock.close()
            first_sock.close()
            sys.exit()

    else:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)          #Client: First sock on port 6001
        sock.connect(('localhost',int(conn_port)))

        try:
            sock.send(lstn_port.encode())
        except:
            sock.close()
            sys.exit()


    revc_thread = threading.Thread(target=msg_recv,args=(sock,))            # Msg recv thread
    revc_thread.start()  

    file_thread = threading.Thread(target=handle_file_req,args=(first_sock,))  # File transfer thread
    file_thread.start()

    while True:
        print("Enter an option ('m', 'f', 'x'): \r")
        print(" (M)essage (send)\r")
        print(" (F)ile (request)\r")
        print("e(x)it\r")
        option = input()
    
        if(option == 'm'):
            print('Enter message: ')
            msg = input()
            if not msg:
                break
            try:
                sock.send(msg.encode())
            except:
                break
        elif(option == 'f'):
            print('Enter file name')
            file_name = input().rstrip('\n')
            if not file_name:
                break
            file_recv_thread = threading.Thread(target=file_recv,args=(server_addr,conn_port,file_name,))  # File transfer thread
            file_recv_thread.start()
            
        elif(option == 'x'):
            break
        else:
            print("Wrong input")
    try:
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        first_sock.close()
        os._exit(0)
    except:
        pass

if __name__ == "__main__":
    main()
