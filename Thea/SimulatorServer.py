import sys
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

robot: Moto = Moto(
        "localhost",
        [ControlGroupDefinition("robot", 0, 6, ["s", "l", "u", "r", "b", "t"])],
    )

time.sleep(1)

position = robot.state.joint_feedback(0).pos
print("------------------joint position")
print(position)

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

    s.set_writable()
    l.set_writable()
    u.set_writable()
    r.set_writable()
    b.set_writable()
    t.set_writable()

    # starting!
    server.start()
    print("server is started")
    try:

        while True:

            time.sleep(0.1)
            s.set_value(position[0])
            l.set_value(position[1])
            u.set_value(position[2])
            r.set_value(position[3])
            b.set_value(position[4])
            t.set_value(position[5])
    
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
