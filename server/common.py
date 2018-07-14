
import uuid
import platform
from server.models.status import Status

global Version
global Hostname

Version = "0.0.1"
Hostname = platform.node()

def init():
    global Token
    global MeArm
    global Status

    Token = None
    MeArm = None
    Status = Status(Hostname, Version, False)
