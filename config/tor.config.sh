#!/bin/bash

source tor.config

# check whether package is installed
packages="hostapd dnsmasq"
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

# tell dhcpcd ignore wlan0
hasDenyWlan0=$(grep "^denyinterfaces wlan0" /etc/dhcpcd.conf)
if [ ! -n "$hasDenyWlan0" ]; then
	echo "denyinterfaces wlan0" >> /etc/dhcpcd.conf
fi

# set wlan0 static ip
cat <<EOT > /etc/network/interfaces
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d

auto lo
iface lo inet loopback

iface eth0 inet manual

allow-hotplug wlan0
iface wlan0 inet static
    address $tor_wlan0_address
    netmask $tor_wlan0_netmask
    network $tor_wlan0_network
    broadcast $tor_wlan0_broadcast

allow-hotplug wlan1
iface wlan1 inet manual
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
EOT

# configure hostapd
cat <<EOT > /etc/hostapd/hostapd.conf
# This is the name of the WiFi interface we configured above
interface=wlan0

# Use the nl80211 driver with the brcmfmac driver
driver=nl80211

# This is the name of the network
ssid=$tor_hostapd_ssid

# Use the 2.4GHz band
hw_mode=g

# Use channel
channel=$tor_hostapd_channel

# Enable 802.11n
ieee80211n=1

# Enable WMM
wmm_enabled=1

# Enable 40MHz channels with 20ns guard interval
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]

# Accept all MAC addresses
macaddr_acl=0

# Use WPA authentication
auth_algs=1

# Require clients to know the network name
ignore_broadcast_ssid=0

# Use WPA2
wpa=2

# Use a pre-shared key
wpa_key_mgmt=WPA-PSK

# The network passphrase
wpa_passphrase=$tor_hostapd_password

# Use AES, instead of TKIP
rsn_pairwise=CCMP
EOT

# tell hostapd where to look for the config file
hasConfigHostapd=$(grep "^DAEMON_CONF" /etc/default/hostapd)
if [ ! -n "$hasConfigHostapd" ]; then
	sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="/etc/hostapd/hostapd.conf"' /etc/default/hostapd
fi

# configure dnsmasq
cat <<EOT > /etc/dnsmasq.conf
# Use interface
interface=$tor_interface
# Explicitly specify the address to listen on
listen-address=$tor_listen_address
# Bind to the interface to make sure we aren't sending things elsewhere
bind-interfaces
# Forward DNS requests
server=$tor_nameserver
# Don't forward short names
domain-needed
# Never forward addresses in the non-routed address spaces.  
bogus-priv   
# Assign IP addresses
dhcp-range=$tor_dhcp_range
EOT

# enable ip forward
sysctl -w net.ipv4.ip_forward=1

# configure nat network
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE  
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT  
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT  

echo "wait for 5 seconds..."
sleep 5

# store the iptables
iptables-save > /etc/iptables.ipv4.nat
# check iptable-restore
hasRestore=$(grep "iptables-restore" /etc/rc.local)
if [ ! -n "$hasRestore" ]; then
	sed -i -e '$i \iptables-restore < /etc/iptables.ipv4.nat\n' /etc/rc.local
fi