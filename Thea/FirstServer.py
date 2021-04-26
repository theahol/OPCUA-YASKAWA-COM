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

#Connect to physical robot with IP address 192.168.255.200
robot: Moto = Moto(
        "192.168.255.200",
        [ControlGroupDefinition("robot", 0, 6, ["s", "l", "u", "r", "b", "t"])],
    )

    
#Connect to moto simulation with localhost
'''
robot: Moto = Moto(
        "localhost",
        [ControlGroupDefinition("robot", 0, 6, ["s", "l", "u", "r", "b", "t"])],
    )'''

robot.motion.start_servos()
robot.motion.start_trajectory_mode()

status = robot.motion.check_motion_ready()
print("---------------------status of robot ready/not ready?: ")
print(status)

position = robot.state.joint_feedback(0).pos
print("---------------------current position of robot joints: ")
print(position)

# update current position
p0 = JointTrajPtFull(
            groupno=0,
            sequence=0,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=0,
            pos = position,
            vel = [0.0]*10,
            acc=robot.state.joint_feedback(0).acc
        )
robot.motion.send_joint_trajectory_point(p0)
time.sleep(1)

#define new position
p1 = JointTrajPtFull(
            groupno=0,
            sequence=1,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=10.0,
            pos=np.deg2rad([40.0, 0.0, 0.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10
        )
robot.motion.send_joint_trajectory_point(p1) 
time.sleep(4)

#Check if robot is still moving, if true --> await 
  '''
  check = robot.state.robot_status().in_motion
  print(check)
  time.sleep(5)

  check = robot.state.robot_status().in_motion
  print(check)
  time.sleep(2)'''


position2 = robot.state.joint_feedback(0).pos
print("------------------Updated joint pos after movement")
print(position2)

print("------------------joint pos in deg after movement: ")
print(np.rad2deg(position2))

def disconnect(self):
    client.close()

if __name__ == "__main__":

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://10.24.11.202:4840/motopcua/server/")

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
            s.set_value(np.rad2deg(position2[0]))
            l.set_value(np.rad2deg(position2[1]))
            u.set_value(np.rad2deg(position2[2]))
            r.set_value(np.rad2deg(position2[3]))
            b.set_value(np.rad2deg(position2[4]))
            t.set_value(np.rad2deg(position2[5]))
    
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
