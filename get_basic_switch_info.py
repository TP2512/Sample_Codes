import getpass
import telnetlib

HOST = "192.168.122.220"  #any IP address
user = input("Enter your username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")


tn.write(b"enable\n")  #considering switch already configured( IP and username and password for the user and enable mode
tn.write(b"passwd\n")
tn.write(b"conf t\n")
tn.write(b"host S1\n")
tn.write(b"end\n")
tn.write(b"terminal length 0\n")
tn.write(b"show running-config\n")
tn.read_until(b"S1#", timeout=5)
tn.write(b"exit\n")
