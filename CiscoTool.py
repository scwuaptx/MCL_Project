import telnetlib
import os
import subprocess
import time
import getpass

Password = ""
host = ""

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
    result = connect.read_all().split("\n")
    macmap = result[7]
    tmp = macmap.split()
    port = tmp[3]
    connect.close()
    if act == "port" :
        return port
    else :
        return macmap

def IPtoMac(IP) :
    cmd = "ping -c 1 " + IP + " > /dev/null" 
    os.system(cmd)
    arpmsg = os.popen("arp -a " + IP).read().split()
    return arpmsg[3]

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

if __name__ == '__main__':

    host = raw_input(">>> Enter host : ")
    Password = getpass.getpass(">>> Password : ")
    try :
        login(Password)
    except :
        print "Error Host or Password"
        exit()

    print """Choose your action :
    1.detect mac address with IP    
    2.detect mac address from port
    3.ban mac address
    4.no ban mac address
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
    else :
        print "Please choose number 1 to 3."
