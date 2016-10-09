#!/bin/bash

source server.config
# echo $server_br0_bridge_ports

# check whether package is installed
packages="dnsmasq bridge-utils"
packagesArray=($packages)
packagesNum=${#packagesArray[@]}
for ((i=0; i<packagesNum; i++)) do
	echo "check for ${packagesArray[$i]} installation status"
	isInstall=$(dpkg -l ${packagesArray[$i]} | grep ${packagesArray[$i]})
	if [ -n "$isInstall" ]; then
		echo -e "\t${packagesArray[$i]} was installed."
	else
		echo -e "\t${packagesArray[$i]} was not installed. trying to install it..."
		# apt-get install ${packagesArray[$i]}
	fi
done

# enable ip forward
# sysctl -w net.ipv4.ip_forward=1

# configurate br0 with nat network
# iptables -t nat -A POSTROUTING -o br0 -j MASQUERADE
# iptables -A FORWARD -i br0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
# iptables -A FORWARD -i wlan0 -o br0 -j ACCEPT