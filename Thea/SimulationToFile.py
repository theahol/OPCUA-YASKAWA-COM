import sys
import csv
import socket
sys.path.insert(0, "..")
import time
from moto.simple_message import *
from moto import motion_connection
from moto.simple_message_connection import SimpleMessageConnection
from moto.simple_message import SimpleMessage
from moto import Moto
from moto import Moto, ControlGroupDefinition
from moto.simple_message import (
    JointFeedbackEx,
    JointTrajPtExData,
    JointTrajPtFull,
    JointTrajPtFullEx,
)
import copy
from opcua import ua, Server
import numpy as np
import json


def trajectory_continuing(pos_vec, history_vec):

    history_vec.append(pos_vec)

    if len(history_vec) <= 4:
        continuing = True
        return history_vec, continuing
    
    else:

        temp = np.asarray(history_vec[-4:])
        print(temp)
        print(temp.shape)

        if sum(abs(temp[-1])-abs(temp[-2])) < 10**-3 and sum(abs(temp[-1])-abs(temp[-3])) < 10**-3 and sum(abs(temp[-1])-abs(temp[-4])) < 10**-3:
            continuing = False
            return history_vec, continuing

        else:
            continuing = True
            return history_vec, continuing



def disconnect(self):
    client.close()

if __name__ == "__main__":

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://10.24.10.62:4840/motopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://server.motopcua.github.io"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # populating our address space
    myobj = server.nodes.objects.add_object(idx, "Moto")
    myvar = myobj.add_variable(idx, "MyVariable", 6.7)

    myvar.set_writable()    # Set MyVariable to be writable by clients
    
    # Adding desired variables
    s = myobj.add_variable(idx, "s", 6.7)
    l = myobj.add_variable(idx, "l", 6.7)
    u = myobj.add_variable(idx, "u", 6.7)
    r = myobj.add_variable(idx, "r", 6.7)
    b = myobj.add_variable(idx, "b", 6.7)
    t = myobj.add_variable(idx, "t", 6.7)
    clock = myobj.add_variable(idx, "clock", 1)

    s.set_writable()
    l.set_writable()
    u.set_writable()
    r.set_writable()
    b.set_writable()
    t.set_writable()
    clock.set_writable()

    

    # starting!
    server.start()
    print("server is started")
    try:
        pos_vec = []
        history_vec = []
        data_vec = []
        time_vec = []
        count = 1

        filename = "Thea/joint_values_from_sim03.json"
        start_time = time.time()
        while True:

            time.sleep(0.1)
            new_s = s.get_value()
            new_l = l.get_value()
            new_u = u.get_value()
            new_r = r.get_value()
            new_b = b.get_value()
            new_t = t.get_value()
            timer = clock.get_value()
            

            if new_s != 6.7 or new_l != 6.7 or new_u != 6.7 or new_r != 6.7 or new_b != 6.7 or new_t != 6.7:
                
                prev_time = start_time

                if count > 1:
                    time_var = prev_time-start_time
                    time_vec.append(time_var)

                start_time = time.time()

                vec = [new_s, new_l, new_u, new_r, new_b, new_t]
                
                history_vec, continuing = trajectory_continuing(pos_vec=vec, history_vec=history_vec)
                #if new_s == new_s-1 and new_l == new_l-1 etc så må den vente
                if continuing:

                    data = json.load(open(filename))
                    
                    if count != 1:
                        data_vec = data["joint_values"]
                    
                    data_vec.append(vec)

                    data["joint_values"] = data_vec 
                    #print(type(data))
                    #print(data)

                    with open(filename, "w") as f:
                        json.dump(data, f, indent=2)
                
                    pos_vec.append(vec)
                else:
                    time_vec_final = time_vec[0:-1]
                
                count += 1

                if count>3 and new_s == 0.0 and new_l == 0.0 and new_u == 0.0 and new_r == 0.0 and new_b == 0.0 and new_t == 0.0:
                    print("tajectory finished")
                    server.stop()
                

 
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()


