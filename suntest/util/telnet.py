# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
# Filename: telnet.py
# Author: huangbin@pset.suntec.net
# Date: 2014.1.17
# Input:
#       src_p: source path
#       tgt_ld: target load name, it can be a file or folder
#       tgt_p: target path
#------------------------------------------------------------------------------
import sys
import telnetlib


def TelnetLogin(HOST=None, PORT=None, USERNAME=None, PASSWORD=None, COMMAND=None, TIMEOUT=None):
    if not HOST:
        try:
            HOST = sys.argv[1]
            PORT = sys.argv[2]
            USERNAME = sys.argv[3]
            PASSWORD = sys.argv[4]
            COMMAND = sys.argv[5]
            TIMEOUT = sys.argv[6]
        except:
            print "Usage: telnetdo.py host port username password command"
            return
    tn = telnetlib.Telnet(HOST, PORT)
    if PORT:
        if TIMEOUT:
            tn = telnetlib.Telnet(HOST, PORT, TIMEOUT)
        else:
            tn = telnetlib.Telnet(HOST, PORT)
    else:
        tn = telnetlib.Telnet(HOST)
    if USERNAME:
        tn.read_until("login:")
        tn.write(USERNAME + '\n')
    if PASSWORD:
        tn.read_until("Password:")
        tn.write(PASSWORD + '\n')
    if COMMAND:
        tn.write(COMMAND + '\n')
        tn.write("exit\n")
    print tn.read_all()
    #tmp = tn.read_all()
    tn.close()
    del tn
    #return tmp


def main(argv):
    host = "172.26.188.204"
    port = None
    username = "webcloud"
    password = "webcloud"
    command = "ls"
    timeout = None

    TelnetLogin(host, port, username, password, command, timeout)

if __name__ == "__main__":
    main(sys.argv)
