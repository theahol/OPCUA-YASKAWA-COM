import sys
import socket
sys.path.insert(0, "..")
import time
from moto import Moto
from moto import ControlGroupDefinition

from opcua import ua, Server
#robotip:192.168.255.200

#m er et object(?) i/av klassen Moto
'''m = Moto(
    "localhost",
    [
        ControlGroupDefinition(
            groupid="R1",
            groupno=0,
            num_joints=6,
            joint_names=[
                "joint_1_s",
                "joint_2_l",
                "joint_3_u",
                "joint_4_r",
                "joint_5_b",
                "joint_6_t",
            ],
        ),
    ],
)'''
robot: Moto = Moto(
        "localhost",
        [ControlGroupDefinition("robot", 0, 6, ["s", "l", "u", "r", "b", "t"])],
    )

'''r1 = m.control_groups["R1"]
print(r1.position)

#.state er en klasse hvor.joint_feedback_ex() er en method 
#robot_joint_feedback = m.state.joint_feedback_ex()

#p0 er et object som lages fra/i class JointTrajPtFullEx. Class JointTra.... ligger i moto/simple_message.py
p0 = JointTrajPtFullEx(
    number_of_valid_groups=2,
    sequence=0,
    joint_traj_pt_data=[
        JointTrajPtExData(
            groupno=0,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=0.0,
            pos=robot_joint_feedback.joint_feedback_data[0].pos,
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
    ],
)

p1 = JointTrajPtFullEx(
    number_of_valid_groups=2,
    sequence=1,
    joint_traj_pt_data=[
        JointTrajPtExData( #JointTrajPtExData er en egen klasse linje 493 simple_message
            groupno=0,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=5.0,
            pos=np.deg2rad([10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
    ],
)

m.motion.send_trajectory_point(p0) # Current position at time t=0.0
m.motion.send_trajectory_point(p1) # Desired position at time t=5.0'''

if __name__ == "__main__":

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''robot: Moto = Moto(
        robot_ip,
        [ControlGroupDefinition("robot", 0, 6, ["s", "l", "u", "r", "b", "t"])],
    )'''

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://localhost:4840/motopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://server.motopcua.github.io"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # populating our address space
    myobj = server.nodes.objects.add_object(idx, "Moto")
    myvar = myobj.add_variable(idx, "MyVariable", 6.7)

    myvar.set_writable()    # Set MyVariable to be writable by clients
    myobj.add_method(
        ua.NodeId("StartServos", 2),
        ua.QualifiedName("StartServos", 2),
        func,
        [ua.VariantType.Null],
        [ua.VariantType.Null],
    )

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
    
    try:
        count = 0
        while True:
            time.sleep(1)
            count += 0.1
            myvar.set_value(count)
            print(count)
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()