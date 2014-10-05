#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telnetlib
import os
import time
import getpass
import re


Password = ""
host = ""
aclpool = ["m115","m417","m313","m201","m208"]

def login(Password) :
    username = ""
    connect = telnetlib.Telnet(host)

    #connect.read_until("Username:")
    #connect.write(username + "\n")

    connect.read_until("Password: ")
    connect.write(Password + "\n")
    return connect

def macfrom(mac,act="macmap") :
    connect = login(Password)
    connect.write("show mac address-table address " + mac + "\n")
    connect.write("exit\n")
    result = connect.read_all()
    pat = r".*\..*\..*"
    match = re.search(pat,result)
    if match :
        macmap = match.group()
        pat = r"Gi1\/0\/.*"
        tmp = re.search(pat,macmap)
        port = tmp.group()
        connect.close()
        if act == "port" :
            return port
        else :
            return macmap
    else :
        return "Not fround"

def IPtoMac(IP) :
    cmd = "ping -c 1 " + IP + " > /dev/null" 
    os.system(cmd)
    arpmsg = os.popen("arp -a " + IP).read()
    pat = r"..:..:..:..:..:.."
    mac = re.search(pat,arpmsg)
    if mac :
        return mac.group()
    else :
        return "Not fround"

def BanMac(mac,act="disable") :
    maclist = macfrom(mac)
    detaillist = maclist.split()
    vlan = detaillist[0]
    if act == "enable" :
        cmd_list = ["en",Password,"conf ter",
        "mac address-table static " + mac + " vlan " + vlan + " drop",
        "exit","exit"]
    else :
        cmd_list = ["en",Password,"conf ter",
        "no mac address-table static " + mac + " vlan " + vlan + " drop",
        "exit","exit"]
    connect = login(Password)
    #connect.set_debuglevel(2)
    for cmd in cmd_list :
        connect.write(cmd + "\n")
        time.sleep(0.1)
    connect.close()
    try :
        maclist = macfrom(mac)
        detaillist = maclist.split()
        status = detaillist[2]
    except :
        if act == "disable" :
            return "Sucessful"
        else :
            return "Error ban"

    if act == "enable" and status == "STATIC":
        return "Sucessful"
    elif act == "enable" and status == "DYNAMIC":
        return "Still connect"
    elif act == "disable" and status == "STATIC" :
        return "Still disconnect"
    else :
        return "Error"
def showacl(NameofACL):
    cmd = "sh access-lists " + NameofACL
    connect = login(Password)
    connect.write(cmd + "\n")
    connect.write(" ")
    connect.write("exit\n")
    result = connect.read_all()
    return result

def appendacl(NameofACL,IP) :
    cmd_list = ["en",Password,"conf ter",
            "ip access-list extended " + NameofACL,
            "permit ip host " + IP + " any","exit","exit","exit" ]
    connect = login(Password)
    for cmd in cmd_list :
        connect.write(cmd + "\n")
        time.sleep(0.1)
    connect.close()
    acl = showacl(NameofACL)
    if re.search(IP,acl) :
        print "Sucessful"
    else :
        print "Fault"

def removeacl(NameofACL,IP) :
    cmd_list = ["en",Password,"conf ter",
            "ip access-list extended " + NameofACL,
            "no permit ip host " + IP + " any","exit","exit","exit" ]
    connect = login(Password)
    for cmd in cmd_list :
        connect.write(cmd + "\n")
        time.sleep(0.1)
    connect.close()
    acl = showacl(NameofACL)
    if re.search(IP,acl) :
        print "Fault"
    else :
        print "Sucessful"

if __name__ == '__main__':

    host = raw_input(">>> Enter host : ")
    Password = getpass.getpass(">>> Password : ")
    try :
        login(Password)
    except :
        print "Error Host or Password"
        exit()
    while 1 :
        print """Choose your action :
            1.detect mac address with IP    
            2.detect mac address from port
            3.ban mac address
            4.no ban mac address
            v-----------L3 Switch------------v
            5.Show Access list
            6.Append IP to Access List
            7.Remove IP in Access List
            ^-----------L3 Switch------------^
            8.exit()
         """
    
        choose = raw_input(">>> Your choose :")

        if choose == "1" :
            print "detect mac address with IP"
            IP = raw_input(">>> Enter a IP address : ")
            mac = IPtoMac(IP)
            print "The mac address is %s " % mac
        elif choose == "2" :
            print "detect mac address from port"
            mac = raw_input(">>> Enter a mac address : ")
            port = macfrom(mac,"port")
            print port
        elif choose == "3" :
            print "Ban mac address"
            mac = raw_input(">>> Enter a mac address : ")
            result = BanMac(mac,"enable")
            print result
        elif choose == "4" :
            print "no Ban mac address"
            mac = raw_input(">>> Enter a mac address : ")
            result = BanMac(mac,"disable")
            print result 
        elif choose == "5" :
            print "Show Access List"
            NameofACL = raw_input(">>> Enter a name of ACL : ")
            if NameofACL in aclpool :
                print showacl(NameofACL)
            else :
                print NameofACL + " is empty."
        elif choose == "6" :
            print "Apppend IP to Access List"
            NameofACL = raw_input(">>> Enter a name of ACL : ")
            if NameofACL in aclpool :
                IP  = raw_input(">>> Enter a IP : ")
                appendacl(NameofACL,IP)
            else :
                print NameofACL + " is empty."
        elif choose == "7" :
            print "Remove IP in Access List"
            NameofACL = raw_input(">>> Enter a name of ACL : ")
            if NameofACL in aclpool :
                IP  = raw_input(">>> Enter a IP : ")
                removeacl(NameofACL,IP)
            else :
                print NameofACL + " is empty."
        elif choose == "8" :
            exit()
        else :
            print "Please choose number 1 to 8."
        print "<------------------------------------------>"
