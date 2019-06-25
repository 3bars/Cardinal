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

import mysql.connector
import os
import subprocess
from configparser import ConfigParser
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash

# System variables

cardinalConfig = os.environ['CARDINAL_CONFIG']

# Flask app intitialization

Cardinal = Flask(__name__)
Cardinal.secret_key = "SECRET_KEY_HERE"

# MySQL authentication

mysqlConfig = ConfigParser()
mysqlConfig.read("{}".format(cardinalConfig))
mysqlHost = mysqlConfig.get('cardinal_mysql_config', 'servername')
mysqlUser = mysqlConfig.get('cardinal_mysql_config', 'username')
mysqlPass = mysqlConfig.get('cardinal_mysql_config', 'password')
mysqlDb = mysqlConfig.get('cardinal_mysql_config', 'dbname')
conn = mysql.connector.connect(host = mysqlHost, user = mysqlUser, passwd = mysqlPass, db = mysqlDb)

# Flask routes

@Cardinal.route("/")
def index():
    if session.get("username") is not None:
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html")

@Cardinal.route("/dashboard")
def dashboard():
    if session.get("username") is not None:
        return render_template("dashboard.html")
    else:
        return redirect(url_for('index'))

@Cardinal.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    loginCursor = conn.cursor()
    loginCursor.execute("SELECT password FROM users WHERE username = '{}';".format(username))
    hash = loginCursor.fetchone()[0]
    loginCursor.close()
    if check_password_hash(hash,password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return 'Authentication failed. Please check your credentials and try again by clicking <a href="/">here</a>.'

@Cardinal.route("/logout")
def logout():
   session.pop('username', None)
   return redirect(url_for('index'))

@Cardinal.route("/add-ap", methods=["GET"])
def addAp():
    if session.get("username") is not None:
        status = request.args.get('status')
        apGroupCursor = conn.cursor()
        apGroupCursor.execute("SELECT ap_group_id,ap_group_name FROM access_point_groups;")
        apGroups = apGroupCursor.fetchall()
        apGroupCursor.close()
        return render_template("add-ap.html", status=status, apGroups=apGroups)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/submit-add-ap", methods=["POST"])
def submitAddAp():
    if request.method == 'POST':
        apName = request.form["ap_name"]
        apIp = request.form["ap_ip"]
        apSshUsername = request.form["ssh_username"]
        apSshPassword = request.form["ssh_password"]
        apGroupId = request.form["group_id"]
        apSnmp = request.form["ap_snmp"]
        status = "Success! {} was successfully registered!".format(apName)
        addApCursor = conn.cursor()
        addApCursor.execute("INSERT INTO access_points (ap_name, ap_ip, ap_ssh_username, ap_ssh_password, ap_snmp, ap_group_id) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}';)".format(apName, apIp, apSshUsername, apSshPassword, apSnmp, apGroupId))
        addApCursor.close()
        conn.commit()
        return redirect(url_for('addAp', status=status))

@Cardinal.route("/delete-ap", methods=["GET"])
def deleteAp():
    if session.get("username") is not None:
        status = request.args.get('status')
        apCursor = conn.cursor()
        apCursor.execute("SELECT ap_id,ap_name FROM access_points;")
        aps = apCursor.fetchall()
        apCursor.close()
        return render_template("delete-ap.html", aps=aps, status=status)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/submit-delete-ap", methods=["POST"])
def submitDeleteAp():
    if request.method == 'POST':
        apId = request.form["ap_id"]
        deleteApNameCursor = conn.cursor()
        deleteApNameCursor.execute("SELECT ap_name FROM access_points WHERE ap_id = '{}';".format(apId))
        apName = deleteApNameCursor.fetchone()[0]
        status = "Success! {} was successfully registered!".format(apName)
        deleteApCursor = conn.cursor()
        deleteApCursor.execute("DELETE FROM access_points WHERE ap_id = '{}'".format(apId))
        deleteApCursor.close()
        conn.commit()
        return redirect(url_for('deleteAp', status=status))

@Cardinal.route("/add-ap-group", methods=["GET"])
def addApGroup():
    if session.get("username") is not None:
        status = request.args.get('status')
        return render_template("add-ap-group.html", status=status)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/submit-add-ap-group", methods=["POST"])
def submitAddApGroup():
    if request.method == 'POST':
        apGroupName = request.form["ap_group_name"]
        status = "Success! {} was successfully registered!".format(apGroupName)
        addApGroupCursor = conn.cursor()
        addApGroupCursor.execute("INSERT INTO access_point_groups (ap_group_name) VALUES ('{}');".format(apGroupName))
        addApGroupCursor.close()
        conn.commit()
        return render_template('add-ap-group.html', status=status)

@Cardinal.route("/delete-ap-group", methods=["GET"])
def deleteApGroup():
    if session.get("username") is not None:
        status = request.args.get('status')
        deleteApGroupCursor = conn.cursor()
        deleteApGroupCursor.execute("SELECT ap_group_id,ap_group_name FROM access_point_groups;")
        apGroups = deleteApGroupCursor.fetchall()
        deleteApGroupCursor.close()
        return render_template("delete-ap-group.html", status=status, apGroups=apGroups)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/submit-delete-ap-group", methods=["POST"])
def submitDeleteApGroup():
    if request.method == 'POST':
        apGroupId = request.form["ap_group_id"]
        deleteApGroupNameCursor = conn.cursor()
        deleteApGroupNameCursor.execute("SELECT ap_group_name FROM access_point_groups WHERE ap_group_id = '{}';".format(apGroupId))
        apGroupName = deleteApGroupNameCursor.fetchone()[0]
        status = "Success! {} was successfully deleted!".format(apGroupName)
        deleteApGroupCursor = conn.cursor()
        deleteApGroupCursor.execute("DELETE FROM access_point_groups WHERE ap_group_id = '{}';".format(apGroupId))
        deleteApGroupCursor.close()
        conn.commit()
        return redirect(url_for('deleteApGroup', status=status))

@Cardinal.route("/network-tools", methods=["GET"])
def networkTools():
    if session.get("username") is not None:
        return render_template("network-tools.html")
    else:
        return redirect(url_for('index'))

@Cardinal.route("/tools-output", methods=["GET"])
def networkToolsOutput():
    if session.get("username") is not None:
        commandOutput = request.args.get("commandOutput")
        return render_template("network-tools-output.html", commandOutput=commandOutput)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/do-nmap", methods=["POST"])
def doNmap():
    if request.method == 'POST':
        ip = request.form["network_ip"]
        commandOutput = subprocess.check_output("nmap -v -A {}".format(ip), shell=True)
        return redirect(url_for('networkToolsOutput', commandOutput=commandOutput))

@Cardinal.route("/do-ping", methods=["POST"])
def doPing():
    if request.method == 'POST':
        ip = request.form["network_ip"]
        commandOutput = subprocess.check_output("ping -c 4 {}".format(ip), shell=True)
        return redirect(url_for('networkToolsOutput', commandOutput=commandOutput))

@Cardinal.route("/do-tracert", methods=["POST"])
def doTracert():
    if request.method == 'POST':
        ip = request.form["network_ip"]
        commandOutput = subprocess.check_output("traceroute {}".format(ip), shell=True)
        return redirect(url_for('networkToolsOutput', commandOutput=commandOutput))

@Cardinal.route("/do-dig", methods=["POST"])
def doDig():
    if request.method == 'POST':
        ip = request.form["network_ip"]
        commandOutput = subprocess.check_output("dig {}".format(ip), shell=True)
        return redirect(url_for('networkToolsOutput', commandOutput=commandOutput))

@Cardinal.route("/do-curl", methods=["POST"])
def doCurl():
    if request.method == 'POST':
        ip = request.form["network_ip"]
        commandOutput = subprocess.check_output("curl -I {}".format(ip), shell=True)
        return redirect(url_for('networkToolsOutput', commandOutput=commandOutput))

@Cardinal.route("/choose-ap-dashboard", methods=["GET"])
def chooseApDashboard():
    if session.get("username") is not None:
        apCursor = conn.cursor()
        apCursor.execute("SELECT ap_id,ap_name FROM access_points;")
        aps = apCursor.fetchall()
        apCursor.close()
        return render_template("choose-ap-dashboard.html", aps=aps)
    else:
        return redirect(url_for('index'))
    
@Cardinal.route("/manage-ap-dashboard", methods=["POST"])
def manageApDashboard():
    if request.method == 'POST':
        apId = request.form["ap_id"]
        apInfoCursor = conn.cursor()
        apInfoCursor.execute("SELECT ap_name,ap_ip,ap_total_clients,ap_bandwidth FROM access_points WHERE ap_id = '{}';".format(apId))
        apInfo = apInfoCursor.fetchall()
        for info in apInfo:
            apName = info[0]
            apIp = info[1]
            apTotalClients = info[2]
            apBandwidth = info[3]
        session['apName'] = apName
        session['apIp'] = apIp
        session['apTotalClients'] = apTotalClients
        session['apBandwidth'] = apBandwidth
        apInfoCursor.close()
        return render_template("manage-ap-dashboard.html")
    else:
        return redirect(url_for('index'))

@Cardinal.route("/choose-ap-group-dashboard", methods=["GET"])
def chooseApGroupDashboard():
    if session.get("username") is not None:
        apGroupCursor = conn.cursor()
        apGroupCursor.execute("SELECT ap_group_id,ap_group_name FROM access_point_groups;")
        apGroups = apGroupCursor.fetchall()
        apGroupCursor.close()
        return render_template("choose-ap-group-dashboard.html", apGroups=apGroups)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/manage-ap-group-dashboard", methods=["POST"])
def manageApGroupDashboard():
    if request.method == 'POST':
        apGroupId = request.form["ap_group_id"]
        apGroupInfoCursor = conn.cursor()
        apGroupInfoCursor.execute("SELECT ap_group_name FROM access_point_groups WHERE ap_group_id = '{}';".format(apGroupId))
        apGroupInfo = apGroupInfoCursor.fetchall()
        for info in apGroupInfo:
            apGroupName = info[0]
        session['apGroupName'] = apGroupName
        apGroupInfoCursor.close()
        return render_template("manage-ap-group-dashboard.html")
    else:
        return redirect(url_for('index'))

@Cardinal.route("/config-ap-ip", methods=["GET"])
def configApIp():
    if session.get("username") is not None:
        return render_template("config-ap-ip.html")

#@Cardinal.route("/do-config-ap-ip", methods=["POST"])
#def doConfigApIp():
#    if request.method == 'POST':
#        apIp = session

@Cardinal.route("/total-ap-clients", methods=["GET"])
def totalApClients():
    if session.get("username") is not None:
        return render_template("total-ap-clients.html")

@Cardinal.route("/total-ap-bandwidth", methods=["GET"])
def totalApBandwidth():
    if session.get("username") is not None:
        return render_template("total-ap-bandwidth.html")
   
@Cardinal.route("/total-aps", methods=["GET"])
def totalAps():
    if session.get("username") is not None:
        totalApsCursor = conn.cursor(buffered=True)
        totalApsCursor.execute("SELECT * FROM access_points;")
        totalAps = totalApsCursor.rowcount
        totalApsCursor.close()
        return render_template('total-aps.html', totalAps=totalAps)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/total-clients", methods=["GET"])
def totalClients():
    if session.get("username") is not None:
        totalClientsCursor = conn.cursor(buffered=True)
        totalClientsCursor.execute("SELECT SUM(ap_total_clients) AS totalClients FROM access_points WHERE ap_all_id = 2;")
        totalClients = totalClientsCursor.fetchone()[0]
        totalClientsCursor.close()
        return render_template('total-clients.html', totalClients=totalClients)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/total-ap-groups", methods=["GET"])
def totalApGroups():
    if session.get("username") is not None:
        totalApGroupsCursor = conn.cursor(buffered=True)
        totalApGroupsCursor.execute("SELECT COUNT(*) AS totalAPGroups FROM access_point_groups;")
        totalApGroups = totalApGroupsCursor.fetchone()[0]
        totalApGroupsCursor.close()
        return render_template('total-ap-groups.html', totalApGroups=totalApGroups)
    else:
        return redirect(url_for('index'))

@Cardinal.route("/total-ssids", methods=["GET"])
def totalSsids():
    if session.get("username") is not None:
        ssids24Cursor = conn.cursor(buffered=True)
        ssids5Cursor = conn.cursor(buffered=True)
        ssids24RadiusCursor = conn.cursor(buffered=True)
        ssids5RadiusCursor = conn.cursor(buffered=True)
        ssids24Cursor.execute("SELECT COUNT(*) FROM ssids_24ghz;")
        ssids5Cursor.execute("SELECT COUNT(*) FROM ssids_5ghz;")
        ssids24RadiusCursor.execute("SELECT COUNT(*) FROM ssids_24ghz_radius;")
        ssids5RadiusCursor.execute("SELECT COUNT(*) FROM ssids_5ghz_radius;")
        ssids24 = ssids24Cursor.fetchone()[0]
        ssids5 = ssids5Cursor.fetchone()[0]
        ssids24Radius = ssids24RadiusCursor.fetchone()[0]
        ssids5Radius = ssids5RadiusCursor.fetchone()[0]
        totalSsids = ssids24 + ssids5 + ssids24Radius + ssids5Radius
        ssids24Cursor.close()
        ssids5Cursor.close()
        ssids24RadiusCursor.close()
        ssids5RadiusCursor.close()
        return render_template('total-ssids.html', totalSsids=totalSsids)
    else:
        return redirect(url_for('index'))

if __name__ == "__main__":
    Cardinal.run(debug=True, host='0.0.0.0')
