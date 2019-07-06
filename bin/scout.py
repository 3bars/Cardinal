#!/usr/bin/env python3

''' Cardinal - An Open Source Cisco Wireless Access Point Controller

MIT License

Copyright © 2019 Cardinal Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import os
import time
import jinja2
import subprocess
import paramiko
import sys
import MySQLdb
from configparser import ConfigParser

# CARDINAL SETTINGS

cardinalConfigFile = os.environ['CARDINALCONFIG']
cardinalConfig = ConfigParser()
cardinalConfig.read("{}".format(cardinalConfigFile))

# BEGIN CARDINAL SETTING DECLARATIONS

mysqlHost = cardinalConfig.get('cardinal', 'dbserver')
mysqlUser = cardinalConfig.get('cardinal', 'username')
mysqlPass = cardinalConfig.get('cardinal', 'password')
mysqlDb = cardinalConfig.get('cardinal', 'dbname')
commandDir = cardinalConfig.get('cardinal', 'commanddir')

# CARDINAL SYSTEM VARIABLES

fileLoader = jinja2.FileSystemLoader('{}'.format(commandDir))
env = jinja2.Environment(loader=fileLoader)
scoutCommand = sys.argv[1]

# MySQL CONNECTION

conn = MySQLdb.connect(host = mysqlHost, user = mysqlUser, passwd = mysqlPass, db = mysqlDb)

# SSH INFORMATION

def connInfo():
    ip = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    scoutSsh = paramiko.SSHClient()
    scoutSsh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    scoutSsh.connect(ip, port = 22, username = username, password = password, look_for_keys = False, allow_agent = False)
    return ip, username, password, scoutSsh

# SCOUT HELP & USAGE

if scoutCommand == "--help":
    print("Scout: Cardinal CLI for managing Cisco access points")
    print("Usage:")
    print("   scout.py --get-arp: print access point ARP table")
    print("   scout.py --led: trigger LED function for 30 seconds")
    print("   scout.py --change-ip: change access point IP")
    print("   scout.py --create-ssid-24: create a 2.4GHz SSID")
    print("   scout.py --create-ssid-5: create a 5GHz SSID")
    print("   scout.py --create-ssid-radius-24: create a 2.4GHz RADIUS SSID")
    print("   scout.py --create-ssid-radius-5: create a 5GHz RADIUS SSID")
    print("   scout.py --delete-ssid-24: delete a 2.4GHz SSID")
    print("   scout.py --delete-ssid-5: delete a 5GHz SSID")
    print("   scout.py --delete-ssid-radius-24: delete a 2.4GHz RADIUS SSID")
    print("   scout.py --delete-ssid-radius-5: delete a 5GHz RADIUS SSID")
    print("   scout.py --disable-http: disable access point HTTP server")
    print("   scout.py --disable-radius: disable access point RADIUS function") 
    print("   scout.py --disable-snmp: disable access point SNMP function")
    print("   scout.py --enable-http: enable access point HTTP function")
    print("   scout.py --enable-radius: enable access point RADIUS function")
    print("   scout.py --enable-snmp: enable access point SNMP function")
    print("   scout.py --get-speed: show access point link speed")
    print("   scout.py --tftp-backup: backup access point config via TFTP")
    print("   scout.py --wr: write configuration to access point")
    print("   scout.py --erase: erase configuration on access point")
    print("   scout.py --count-clients: fetch client associations on access point")
    print("   scout.py --get-name: fetch access point hostname via SNMP")
    print("   scout.py --ping: ping access point")
    print("   scout.py --get-mac: fetch access point MAC address via SNMP")
    print("   scout.py --get-model: fetch access point model info via SNMP")
    print("   scout.py --get-serial: fetch access point serial number via SNMP")
    print("   scout.py --get-location: fetch access point location via SNMP")
    print("   scout.py --get-ios-info: fetch access point IOS info via SNMP")
    print("   scout.py --get-uptime: fetch access point uptime info via SNMP")
    print("   scout.py --reboot: reboot access point via SNMP")
    print("   scout.py --change-name: change access point hostname")

# cisco_arp.py

if scoutCommand == "--get-arp":
    ip, username, password, scoutSsh = connInfo()
    stdin, stdout, stderr = scoutSsh.exec_command("show ip arp\n")
    arpCommandOutput = stdout.read()
    scoutSsh.close()
    print(arpCommandOutput.decode('ascii').strip("\n"))

# cisco_led.py

if scoutCommand == "--led":
    ip, username, password, scoutSsh = connInfo()
    stdin, stdout, stderr = scoutSsh.exec_command("led flash 30\n")
    scoutSsh.close()

# cisco_change_ap_ip.py

if scoutCommand == "--change-ip":
    ip, username, password, scoutSsh = connInfo()
    newIp = sys.argv[5]
    subnetMask = sys.argv[6]
    cmdTemplate = env.get_template("scout_change_ap_ip")
    cmds = cmdTemplate.render(password=password,newIp=newIp,subnetMask=subnetMask)
    scoutCommands = cmds.splitlines()
    channel = scoutSsh.invoke_shell()
    for command in scoutCommands:
        channel.send('{}\n'.format(command))
        time.sleep(1)
    scoutSsh.close()
    scoutSsh2 = paramiko.SSHClient()
    scoutSsh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    scoutSsh2.connect(newIp, port = 22, username = username, password = password, look_for_keys = False, allow_agent = False)
    cmdTemplate2 = env.get_template("scout_do_wr")
    cmds2 = cmdTemplate.render(password=password)
    scoutCommands2 = cmds2.splitlines()
    channel2 = scoutSsh2.invoke_shell()
    for command2 in scoutCommands2:
        channel2.send('{}\n'.format(command2))
        time.sleep(1)
    scoutSsh2.close()

# cisco_configure_ssid.py

if scoutCommand == "--create-ssid-24":
    ip, username, password, scoutSsh = connInfo()
    ssid = sys.argv[5]
    wpa2Pass = sys.argv[6]
    vlan = sys.argv[7]
    bridgeGroup = sys.argv[8]
    radioSub = sys.argv[9]
    gigaSub = sys.argv[10]
    cmdTemplate = env.get_template("scout_create_ssid_24")
    cmds = cmdTemplate.render(ssid=ssid,wpa2Pass=wpa2Pass,vlan=vlan,bridgeGroup=bridgeGroup,radioSub=radioSub,gigaSub=gigaSub)
    scoutCommands = cmds.splitlines()
    channel = scoutSsh.invoke_shell()
    for command in scoutCommands:
        channel.send('{}\n'.format(command))
        time.sleep(1)
    scoutSsh.close()

# cisco_configure_ssid_5ghz.py

if scoutCommand == "--create-ssid-5":
    ip, username, password, scoutSsh = connInfo()
    ssid = sys.argv[5]
    wpa2Pass = sys.argv[6]
    vlan = sys.argv[7]
    bridgeGroup = sys.argv[8]
    radioSub = sys.argv[9]
    gigaSub = sys.argv[10]
    cmdTemplate = env.get_template("scout_create_ssid_5")
    cmds = cmdTemplate.render(ssid=ssid,wpa2Pass=wpa2Pass,vlan=vlan,bridgeGroup=bridgeGroup,radioSub=radioSub,gigaSub=gigaSub)
    scoutCommands = cmds.splitlines()
    channel = scoutSsh.invoke_shell()
    for command in scoutCommands:
        channel.send('{}\n'.format(command))
        time.sleep(1)
    scoutSsh.close()

# cisco_configure_ssid_radius.py

if scoutCommand == "--create-ssid-radius-24":
    ip, username, password, scoutSsh = connInfo()
    ssid = sys.argv[5]
    vlan = sys.argv[6]
    bridgeGroup = sys.argv[7]
    radioSub = sys.argv[8]
    gigaSub = sys.argv[9]
    radiusIp = sys.argv[10]
    sharedSecret = sys.argv[11]
    authPort = sys.argv[12]
    acctPort = sys.argv[13]
    radiusTimeout = sys.argv[14]
    radiusGroup = sys.argv[15]
    methodList = sys.argv[16]
    cmdTemplate = env.get_template("scout_create_radius_ssid_24")
    cmds = cmdTemplate.render(ssid=ssid,vlan=vlan,bridgeGroup=bridgeGroup,radioSub=radioSub,gigaSub=gigaSub,radiusIp=radiusIp,sharedSecret=sharedSecret,authPort=authPort,acctPort=acctPort,radiusTimeout=radiusTimeout,radiusGroup=radiusGroup,methodList=methodList)
    scoutCommands = cmds.splitlines()
    channel = scoutSsh.invoke_shell()
    for command in scoutCommands:
        channel.send('{}\n'.format(command))
        time.sleep(1)
    scoutSsh.close()

# cisco_configure_ssid_radius_5ghz.py

if scoutCommand == "--create-ssid-radius-5":
    ip, username, password, scoutSsh = connInfo()
    ssid = sys.argv[5]
    vlan = sys.argv[6]
    bridgeGroup = sys.argv[7]
    radioSub = sys.argv[8]
    gigaSub = sys.argv[9]
    radiusIp = sys.argv[10]
    sharedSecret = sys.argv[11]
    authPort = sys.argv[12]
    acctPort = sys.argv[13]
    radiusTimeout = sys.argv[14]
    radiusGroup = sys.argv[15]
    methodList = sys.argv[16]
    cmdTemplate = env.get_template("scout_create_radius_ssid_5")
    cmds = cmdTemplate.render(ssid=ssid,vlan=vlan,bridgeGroup=bridgeGroup,radioSub=radioSub,gigaSub=gigaSub,radiusIp=radiusIp,sharedSecret=sharedSecret,authPort=authPort,acctPort=acctPort,radiusTimeout=radiusTimeout,radiusGroup=radiusGroup,methodList=methodList)
    scoutCommands = cmds.splitlines()
    channel = scoutSsh.invoke_shell()
    for command in scoutCommands:
        channel.send('{}\n'.format(command))
        time.sleep(1)
    scoutSsh.close()

# cisco_delete_ssid.py

if scoutCommand == "--delete-ssid-24":
    ip, username, password, scoutSsh = connInfo()
    ssid = sys.argv[5]
    vlan = sys.argv[6]
    radioSub = sys.argv[7]
    gigaSub = sys.argv[8]
    cmdTemplate = env.get_template("scout_delete_ssid_24")
    cmds = cmdTemplate.render(ssid=ssid,vlan=vlan,radioSub=radioSub,gigaSub=gigaSub)
    scoutCommands = cmds.splitlines()
    channel = scoutSsh.invoke_shell()
    for command in scoutCommands:
        channel.send('{}\n'.format(command))
        time.sleep(1)
    scoutSsh.close()

# cisco_delete_ssid_5ghz.py

if scoutCommand == "--delete-ssid-5":
   ip, username, password, scoutSsh = connInfo()
   ssid = sys.argv[5]
   vlan = sys.argv[6]
   radioSub = sys.argv[7]
   gigaSub = sys.argv[8]
   cmdTemplate = env.get_template("scout_delete_ssid_5")
   cmds = cmdTemplate.render(ssid=ssid,vlan=vlan,radioSub=radioSub,gigaSub=gigaSub)
   scoutCommands = cmds.splitlines()
   channel = scoutSsh.invoke_shell()
   for command in scoutCommands:
       channel.send('{}\n'.format(command))
       time.sleep(1)
   scoutSsh.close()

# cisco_delete_ssid_radius.py

if (scoutCommand == "--delete-ssid-radius-24") or (scoutCommand == "--delete-ssid-radius-5"):
   ip, username, password, scoutSsh = connInfo()
   ssid = sys.argv[5]
   vlan = sys.argv[6]
   radioSub = sys.argv[7]
   gigaSub = sys.argv[8]
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "no dot11 ssid {}\n".format(ssid) + "no int d0.{}\n".format(radioSub) + "no int gi0.{}\n".format(gigaSub) + "int d0\n" + "no encryption vlan {} mode ciphers aes-ccm\n".format(vlan) + "do wr\n")
   scoutSsh.close()

# cisco_disable_http.py

if scoutCommand == "--disable-http":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "no ip http server\n" + "do wr\n")
   scoutSsh.close()

# cisco_disable_radius.py

if scoutCommand == "--disable-radius":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "no aaa new-model\n" + "\n" + "do wr\n")
   scoutSsh.close()

# cisco_disable_snmp.py

if scoutCommand == "--disable-snmp":
   ip, username, password, scoutSsh = connInfo()
   snmp = sys.argv[5]
   location = sys.argv[6]
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "no snmp-server community {} RW\n".format(snmp) + "no snmp-server location {}\n".format(location) + "no snmp-server system-shutdown\n" + "do wr\n")
   scoutSsh.close()

# cisco_enable_http.py

if scoutCommand == "--enable-http":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "ip http server\n" + "do wr\n")
   scoutSsh.close()

# cisco_enable_radius.py

if scoutCommand == "--enable-radius":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "%s\n".format(password) + "conf t\n" + "aaa new-model\n" + "do wr\n")
   scoutSsh.close()

# cisco_enable_snmp.py

if scoutCommand == "--enable-snmp":
   ip, username, password, scoutSsh = connInfo()
   snmp = sys.argv[5]
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "snmp-server community {} RW\n".format(snmp) + "snmp-server system-shutdown\n" + "do wr\n")
   scoutSsh.close()

# cisco_get_speed.py

if scoutCommand == "--get-speed":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("sho int gi0\n")
   sshOut = stdout.read()
   sshBandwidth = sshOut.decode('ascii').strip("\n").split(",")
   getBandwidth = sshBandwidth[9].strip("Mbps")
   bandwidthSqlCursor = conn.cursor()
   bandwidthSql = "UPDATE access_points SET ap_bandwidth = '{0}' WHERE ap_ip = '{1}'".format(getBandwidth,ip)
   bandwidthSqlCursor.execute(bandwidthSql)
   scoutSsh.close()
   conn.commit()

# cisco_tftp_backup.py

if scoutCommand == "--tftp-backup":
   ip, username, password, scoutSsh = connInfo()
   tftpIp = sys.argv[5]
   cmdTemplate = env.get_template("scout_do_tftp_backup")
   cmds = cmdTemplate.render(password=password,tftpIp=tftpIp)
   scoutCommands = cmds.splitlines()
   channel = scoutSsh.invoke_shell()
   for command in scoutCommands:
       channel.send('{}\n'.format(command))
       time.sleep(1)
   scoutSsh.close()

# cisco_wr.py

if scoutCommand == "--wr":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "wr\n")
   scoutSsh.close()

# cisco_write_default.py

if scoutCommand == "--erase":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "write default\n" + "y\n" + "reload\n" + "y\n")
   scoutSsh.close()

# cisco_count_clients.py

if scoutCommand == "--count-clients":
   ip, username, password, scoutSsh = connInfo()
   stdin, stdout, stderr = scoutSsh.exec_command("show dot11 associations\n")
   sshOut = stdout.read()
   countClient = print(sshOut.decode('ascii').strip("\n"))
   getClient = subprocess.check_output("echo {} | grep -o [0-9,a-f][0-9,a-f][0-9,a-f][0-9,a-f].[0-9,a-f][0-9,a-f][0-9,a-f][0-9,a-f].[0-9,a-f][0-9,a-f][0-9,a-f][0-9,a-f] | wc -l".format(countClient), shell=True)
   clientSqlCursor = conn.cursor()
   clientSql = "UPDATE access_points SET ap_total_clients = '{0}' WHERE ap_ip = '{1}'".format(getClient,ip)
   clientSqlCursor.execute(clientSql)
   scoutSsh.close()
   conn.commit()

# --get-name

if scoutCommand == "--get-name":
   ip = connInfo()
   snmp = sys.argv[2]
   getApName = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.1.5.0".format(snmp,ip), shell=True)
   sqlApName = getApName.replace('"', '')
   apNameCursor = conn.cursor()
   apNameSql = "UPDATE access_points SET ap_name = '{0}' WHERE ap_ip = '{1}'" % (sqlApName,ip)
   apNameCursor.execute(apNameSql)
   conn.commit() 

# --get-mac

if scoutCommand == "--get-mac":
   ip = connInfo()
   snmp = sys.argv[2]
   getApMac = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.2.2.1.6.3".format(snmp,ip), shell=True)
   sqlApMac = getApMac.replace('"', '')
   apMacCursor = conn.cursor()
   apMacSql = "UPDATE access_points SET ap_mac_addr = '{0}' WHERE ap_ip = '{1}'".format(sqlApMac,ip)
   apMacCursor.execute(apMacSql)
   conn.commit()

# --ping

if scoutCommand == "--ping":
   ip = connInfo()
   pingAp = subprocess.check_output("ping {} -c 10| head -n 2 | tail -n 1 | awk '{print $7}' | tr -d 'time='".format(ip), shell=True)
   pingApOutput = pingAp.decode(encoding = 'UTF-8')
   pingApCursor = conn.cursor()
   pingApSql = "UPDATE access_points SET ap_ping_ms = '{0}' WHERE ap_ip = '{1}'".format(pingApOutput,ip)
   pingApCursor.execute(pingApSql)
   conn.commit()

# --get-model

if scoutCommand == "--get-model":
   ip = connInfo()
   snmp = sys.argv[2]
   getApModel = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.47.1.1.1.1.13.1".format(snmp,ip), shell=True)
   sqlApModel = getApModel.replace('"', '')
   apModelCursor = conn.cursor()
   apModelSql = "UPDATE access_points SET ap_model = '{0}' WHERE ap_ip = '{1}'".format(sqlApModel,ip)
   apModelCursor.execute(apModelSql)
   conn.commit()

# --get-serial

if scoutCommand == "--get-serial":
   ip = connInfo()
   snmp = sys.argv[2]
   getApSerial = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.47.1.1.1.1.11.1".format(snmp,ip), shell=True)
   sqlApSerial = getApSerial.replace('"', '')
   apSerialCursor = conn.cursor()
   apSerialSql = "UPDATE access_points SET ap_serial = '{0}' WHERE ap_ip = '{1}'" % (sqlApSerial,ip)
   apSerialCursor.execute(apSerialSql)
   conn.commit()

# --get-location

if scoutCommand == "--get-location":
   ip = connInfo()
   snmp = sys.argv[2]
   getApLocation = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.1.6.0".format(snmp,ip), shell=True)
   sqlApLocation = getApLocation.replace('"', '')
   apLocationCursor = conn.cursor()
   apLocationSql = "UPDATE access_points SET ap_location = '{0}' WHERE ap_ip = '{1}'".format(sqlApLocation,ip)
   apLocationCursor.execute(apLocationSql)
   conn.commit()

# --get-ios-info

if scoutCommand == "--get-ios-info":
   ip = connInfo()
   snmp = sys.argv[2]
   getApIos = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.1.1.0".format(snmp,ip), shell=True)
   sqlApIos = getApIos.replace('"', '')
   apIosCursor = conn.cursor()
   apIosSql = "UPDATE access_points SET ap_ios_info = '{0}' WHERE ap_ip = '{1}'".format(sqlApIos,ip)
   apIosCursor.execute(apIosSql)
   conn.commit()

# --get-uptime

if scoutCommand == "--get-uptime":
   ip = connInfo()
   snmp = sys.argv[2]
   getApUptime = subprocess.check_output("snmpget -Oqv -v2c -c {0} {1} iso.3.6.1.2.1.1.3.0".format(snmp,ip), shell=True)
   sqlApUptime = getApUptime.replace('"', '')
   apUptimeCursor = conn.cursor()
   apUptimeSql = "UPDATE access_points SET ap_uptime = '{0}' WHERE ap_ip = '{1}'".format(sqlApUptime,ip)
   apUptimeCursor.execute(apUptimeSql)
   conn.commit()

# --reboot

if scoutCommand == "--reboot":
   ip = connInfo()
   snmp = sys.argv[2]
   subprocess.check_output("snmpset -v2c -c {0} {1} .1.3.6.1.4.1.9.2.9.9.0 i 2".format(snmp,ip), shell=True)

# --change-name

if scoutCommand == "--change-name":
   ip = connInfo()
   username, password, scoutSsh = connInfo()
   apName = sys.argv[5]
   stdin, stdout, stderr = scoutSsh.exec_command("enable\n" + "{}\n".format(password) + "conf t\n" + "hostname {}".format(apName) + "do wr\n")
   apNameCursor = conn.cursor()
   sqlApName = "UPDATE access_points SET ap_name = '{0}' WHERE ap_ip = '{1}'".format(apName,ip)
   apNameCursor.execute(sqlApName)
   scoutSsh.close()
   conn.commit()
