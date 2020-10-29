#!/usr/bin/python3
import os
import paramiko
import time
import sys
import csv
from pandas import DataFrame

ssh_1 = paramiko.SSHClient()
ssh_1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_2 = paramiko.SSHClient()
ssh_2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssid_list ="SSID.txt"
#==========#
Host_1 = "10.72.69.69"
Port_1 = "22"
User_1 = "handt"
Pass_1 = "Dzs1234@"
#==========#
Host_2 = "10.72.71.71"
Port_2 = "22"
User_2 = "daibq"
Pass_2 = "Dzs1234@"
ping_result = []

with open(ssid_list, 'r') as f:
	lines = f.readlines()
	ssid_list = open(ssid_list,"r+")
	ssid_list = ssid_list.read()
	ssid_list = ssid_list.split('\n')
	ssid_list = ssid_list[0:-1]
	print("List of SSID: ",ssid_list)

def ssh_to_pc(ssh,Host,Port,User,Pass):
	print("Connecting to PC1...")
	ssh.connect(Host, Port, User, Pass, timeout = 2)
	print("=== Connected success ===")
	stdin, stdout, stderr = ssh.exec_command("")



def connect_to_ssid(ssid):
	subnet = "192.168.1."
	print("\nConnecting to SSID name {}...".format(ssid))
	stdin, stdout, stderr = ssh.exec_command("netsh wlan connect name={} ssid={}".format(ssid,ssid))
	time.sleep(3)
	status = stdout.readlines()
	status = "".join(status)
	check_status = status.find("successfully")
	if check_status > -1:
		print("=== Connected SSID success ===")
	else:
		print("=== Connected SSID fail ===")
		return -1
	print("\nChecking ip address ...")
	time.sleep(3)
	stdin, stdout, stderr = ssh.exec_command('netsh interface ip show addresses Wi-Fi | find "IP Address"')
	ip_address = stdout.readlines()
	ip_address = "".join(ip_address)
	print(ip_address)
	ip_address = ip_address.find(subnet)
	if ip_address == -1:
		print("=== Get IP address failed ===")
		return -1
	else:
		print("=== Get IP address DHCP successful ===")
	return 0

def ping():
	print("Start to ping SSID...")
	stdin, stdout, stderr = ssh.exec_command("ping 192.168.1.7")
	result = stdout.readlines()
	result = "".join(result)
	print(result)
	test = result.find("Lost = 0")
	if test == -1: 
  		print("=== Ping to local PC failed ===")
  		data = "NOK"
	else :
  		print("=== Ping to local PC success ===")
  		data = "OK"
	print(data)
	ping_result.append(data)
	print(ping_result)

'''
def result_kq():
	print("current:",ssid)
	result = ping_result
	print(result)
	df = DataFrame({"{}".format(ssid):result},index=ssid_list)
	print(df)



def update_result():
	#Add column corresponds to the ssid of remote PC
	df["Remote"] = result
	print("Summary result : ")
	print(df)
	df.to_excel('result.xlsx')
'''
if __name__ == '__main__':
	ssh_to_pc(ssh_1, Host_1, Port_1, User_1, Pass_1)
	ssh_to_pc(ssh_2, Host_2, Port_2, User_2, Pass_2)
	for ssid in ssid_list:
		ret = connect_to_ssid(ssid)
		if ret == -1:
			stdin, stdout, stderr = ssh_2.exec_command('netsh interface ip show addresses Wi-Fi | find "IP Address"')
			sys.exit()
		
		for ssid in ssid_list:
			ret = connect_to_ssid(ssid)
			if ret == -1:
				stdin, stdout, stderr = ssh_1.exec_command('netsh interface ip show addresses Wi-Fi | find "IP Address"')
				sys.exit()
			ping()
		#ssh.close()

		#ping_result.clear()
#		print(ping_result)
		#print(result)
		#df[ssid] = ping_result	
	#print(df)

