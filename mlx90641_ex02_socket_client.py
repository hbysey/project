import socket 

import seeed_mlx9064x
import time
import numpy
CHIP_TYPE = 'MLX90641'
#HOST = '127.0.0.1'
#PORT = 9999
HOST = '192.168.0.31'
PORT = 8080

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.settimeout(5)
client_socket.connect((HOST, PORT))
client_socket.settimeout(None)

def main():
    if CHIP_TYPE == 'MLX90641':
        mlx = seeed_mlx9064x.grove_mxl90641()
        frame = [0] * 192
    elif CHIP_TYPE == 'MLX90640':
        mlx = seeed_mlx9064x.grove_mxl90640()
        frame = [0] * 768  
    #mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_8_HZ  # The fastest for raspberry 4 
    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_2_HZ  # The fastest for raspberry 4 
    time.sleep(1)
    #max_temp = 0.0
    #message = 0.0
    while True:
        #start = time.time()
        mlx.getFrame(frame)
        #print(len(frame))
        #end = time.time()
        max_temp = float(max(frame))
        #print(type(max_temp))
        message = str(round(max_temp, 2))
        print("temp = " , message)
        #print("The time: %f"%(end - start))
        
        #message = input('Enter Message : ')
        #if message == 'quit':
        #	break

        client_socket.send(message.encode()) 
        data = client_socket.recv(1024) 

        print('Received from the server :',repr(data.decode()))
        
        
        
        #time.sleep(2)
        
if __name__  == '__main__':
    main()

client_socket.close()