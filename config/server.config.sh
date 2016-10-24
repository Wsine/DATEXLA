#!/bin/bash

source server.config
eths=$(echo "$server_br0_bridge_ports" | tr ',' ' ')

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
		apt-get install ${packagesArray[$i]}
	fi
done

# bridge three Ethernets
read -p "Please plugin the Ethernets network cards and press enter..."
brctl addbr br0
brctl addif br0 $eths

# configure network interfaces
ethsArray=($eths)
ethsNum=${#ethsArray[@]}
ifaceEths=""
for ((i=0; i<ethsNum; i++)) do
	ifaceEths+="iface ${ethsArray[$i]} inet manual"
	ifaceEths+=$'\n'
done
cat <<EOT > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0 $eths br0
iface eth0 inet dhcp
$ifaceEths
# Bridge setup
iface br0 inet static
    bridge_ports $eths
    address $server_br0_address
    netmask $server_br0_netmask
    network $server_br0_network
    broadcast $server_br0_broadcast

auto wlan0

# static route
up route add -net $tor1_network mask $tor_network_mask br0
up route add -net $tor2_network mask $tor_network_mask br0
up route add -net $tor3_network mask $tor_network_mask br0
EOT

# configure dnsmasq
cat <<EOT > /etc/dnsmasq.conf
# Never forward plain names (without a dot or domain part)
domain-needed
# Never forward addresses in the non-routed address spaces.
bogus-priv

# listen-interface
interface=$server_interface
# listen on by address
listen-address=$server_listen_address
# nameserver
bind-interfaces
server=$server_nameserver

# supply DHCP service
dhcp-range=$server_dhcp_range
EOT

# enable ip forward
hasEnableIpForward=$(grep "^net.ipv4.ip_forward=1" /etc/sysctl.conf)
if [ ! -n "$hasEnableIpForward" ]; then
	sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
fi

# configure br0 with nat network
iptables -t nat -A POSTROUTING -o br0 -j MASQUERADE
iptables -A FORWARD -i br0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o br0 -j ACCEPT