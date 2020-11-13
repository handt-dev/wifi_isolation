#!/usr/bin/python3
import os
import paramiko
import time
import sys
import csv
import json
import xml.etree.ElementTree as ET 
from xml.etree.ElementTree import ElementTree
from pandas import DataFrame

def ssh_to_pc(ssh,Host,Port,User,Pass):
	print("Connecting to {}...".format(Host))
	ssh.connect(Host, Port, User, Pass, timeout = 5)
	print("=== Connected success ===")
	stdin, stdout, stderr = ssh.exec_command("")

def get_host_profile_from_json(json_file):
	with open(json_file) as file:
		data = json.load(file)
	return data

def create_wifi_profile(wifi_profile, passwd):
	config = """<?xml version=\"1.0\"?>
	<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
		<name>"""+wifi_profile+"""</name>
		<SSIDConfig>
			<SSID>
				<name>"""+wifi_profile+"""</name>
			</SSID>
		</SSIDConfig>
		<connectionType>ESS</connectionType>
		<connectionMode>auto</connectionMode>
		<MSM>
			<security>
			<authEncryption>
				<authentication>WPA2PSK</authentication>
				<encryption>AES</encryption>
				<useOneX>false</useOneX>
			</authEncryption>
			<sharedKey>
				<keyType>passPhrase</keyType>
				<protected>false</protected>
				<keyMaterial>"""+passwd+"""</keyMaterial>
			</sharedKey>
			</security>
		</MSM>
	</WLANProfile>"""
	f = open(wifi_profile, 'w')
	f.write(config)
	f.close()
	return str(wifi_profile)

def create_wifi_profile_from_json(json_file):
	wifi_profile_list = []
	with open(json_file) as file:
		data = json.load(file)
	for wifi_entry in data:
		wifi_profile = create_wifi_profile(wifi_entry['SSID'], wifi_entry['Password'])
		wifi_profile_list.append(wifi_profile)
	return wifi_profile_list

def put_file_via_ssh(ssh, file_name):
	ftp_client = ssh.open_sftp()
	remote_file = "D:\\{}".format(file_name)
	ftp_client.put(file_name, remote_file)
	ftp_client.close()

def add_wifi_profile(ssh, wifi_profile, Host):
	print("Add wifi profile {} for PC {}".format(wifi_profile, Host))
	wifi_profile_path = "D:\\\\" + wifi_profile
	stdin, stdout, stderr = ssh.exec_command("netsh wlan add profile filename={} interface=Wi-Fi".format(wifi_profile_path))

def connect_to_ssid(ssh, wifi_profile, Host):
	subnet = "192.168.1."
	print("\nConnecting to SSID name {} of PC {}...".format(wifi_profile,Host))
	stdin, stdout, stderr = ssh.exec_command("netsh wlan connect name={} ssid={}".format(wifi_profile, wifi_profile))
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
	ip_address_index = ip_address.find(subnet)
	ip_address = ip_address[ip_address_index:]
	return ip_address

def ping(ssh, ip_address):
	print("Start to ping SSID ...")
	stdin, stdout, stderr = ssh.exec_command("ping {}".format(ip_address))
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

def summary_result(wifi_profile_list):
	df = DataFrame(index=wifi_profile_list)
	i = 0
	wifi_num = len(wifi_profile_list)
	for wifi_entry in wifi_profile_list : 
		df["{}".format(wifi_entry)]= ping_result[i:i+wifi_num]
		i = i + wifi_num
	print(df)
	df.to_excel('summary_result.xlsx')

def delete_wifi_profile(ssh, wifi_profile):
	stdin, stdout, stderr = ssh.exec_command("del D:{}".format(wifi_profile))
	stdin, stdout, stderr = ssh.exec_command("netsh wlan del profile name={} interface=Wi-Fi".format(wifi_profile))
	check = stdout.readlines()
	check = "".join(check)
	check = check.find("deleted")
	if check > -1 :
		print("Delete profile succesful")
	else :
		print("Already deleted")

if __name__ == '__main__':
	ping_result = []
	ssh_1 = paramiko.SSHClient()
	ssh_1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_2 = paramiko.SSHClient()
	ssh_2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	data = get_host_profile_from_json("host_data.json")
	wifi_profile_list = create_wifi_profile_from_json("wifi_data.json")
	ssh_to_pc(ssh_1,data[0]["Host"],data[0]["Port"],data[0]["User"],data[0]["Pass"])
	ssh_to_pc(ssh_2,data[1]["Host"],data[1]["Port"],data[1]["User"],data[1]["Pass"])
	print("------------------------")
	for wifi_profile in wifi_profile_list:
		put_file_via_ssh(ssh_1, wifi_profile)
		put_file_via_ssh(ssh_2, wifi_profile)
		add_wifi_profile(ssh_1, wifi_profile, data[0]["Host"])
		add_wifi_profile(ssh_2, wifi_profile, data[1]["Host"])
		print("------------------------")
	for wifi_profile in wifi_profile_list:
		ip_address = connect_to_ssid(ssh_2, wifi_profile, data[1]["Host"])
		if ip_address == -1:
			sys.exit()
		for wifi_profile in wifi_profile_list:
			ret = connect_to_ssid(ssh_1, wifi_profile, data[0]["Host"])
			if ret == -1:
				sys.exit()
			ping(ssh_1, ip_address)
	for wifi_profile in wifi_profile_list:
		delete_wifi_profile(ssh_1, wifi_profile)
		delete_wifi_profile(ssh_2, wifi_profile)
	ssh_1.close()
	ssh_2.close()
	summary_result(wifi_profile_list)

# delete wifi_profile file

