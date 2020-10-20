#!/usr/bin/python3
import os
import paramiko
import time
import sys
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def connect_remote():
	print("Connecting to remote PC...")
	Host = "10.72.69.69"
	Port = "22"
	User = "ha.nguyen"
	Pass = "Dzs1234@"
	ssh.connect(Host, Port, User, Pass,timeout=2)
	print("=== Connected remote success ===")
	stdin, stdout, stderr = ssh.exec_command("") 

def connect_SSID():
	subnet = "192.168.1."
	print("\nConnecting to SSID name {}...".format(ssid))
	stdin, stdout, stderr = ssh.exec_command("netsh wlan connect name={} ssid={}".format(ssid,ssid))
	status = stdout.readlines()
	status = "".join(status)
	#print(status)
	#print(status)
	check_status = status.find("successfully")
	#print(test)
	if check_status > -1:
		print("=== Connected SSID success ===")
	else:
		print("=== Connected SSID fail ===")
		return -1
	print("\nChecking ip address ...")
	stdin, stdout, stderr = ssh.exec_command('netsh interface ip show addresses Wi-Fi | find "IP Address"')
	ip_address = stdout.readlines()
	ip_address = "".join(ip_address)
	print(ip_address)
	ip_address = ip_address.find(subnet)
	#print(ip_address)
	if ip_address == -1:
		print("=== Get IP address failed ===")
		print(ip_address)
		return -1
	else:
		print("=== Get IP address DHCP successful ===")
	return 0

def ping():
	print("Start to ping local PC...")
	stdin, stdout, stderr = ssh.exec_command("ping 192.168.1.5")
	result = stdout.readlines()
	result = "".join(result)
	print(result)
	test = result.find("Lost = 0")
	print(test)
	if test == -1: 
  		print("=== Ping to local PC failed ===")
	else :
  		print("=== Ping to local PC success ===")

ssids = ("HANDT_SSID1", "HANDT_SSID2")
connect_remote()
for ssid in ssids:
	connect_SSID()
	ret = connect_SSID()
	if ret == -1:
		sys.exit()   # check detailed , stop script
ping()

