
import os

def ping_host(host):
    command = "ping -c 1 " + host
    os.system(command)

ping_host("127.0.0.1; whoami")
