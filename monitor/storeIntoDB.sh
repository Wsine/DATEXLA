#!/bin/bash

# clear the table
mysql --user="root" --password="crash" --database="datexla_dcn" --execute="truncate docker_stats"
rsh root@192.168.0.2 docker stats --no-stream | sed 1d |
while IFS= read -r line
do
	container_id=$(echo $line | awk '{print $1}')
	cpu_percent=$(echo $line | awk '{print $2}')
	mem_usage=$(echo $line | awk '{print $3" "$4}')
	mem_limit=$(echo $line | awk '{print $6" "$7}')
	mem_percent=$(echo $line | awk '{print $8}')
	net_i=$(echo $line | awk '{print $9" "$10}')
	net_o=$(echo $line | awk '{print $12" "$13}')
	block_i=$(echo $line | awk '{print $14" "$15}')
	block_o=$(echo $line | awk '{print $17" "$18}')
	pids=$(echo $line | awk '{print $19}')
	# echo "$container_id | $cpu_percent | $mem_usage | $mem_limit | $mem_percent | $net_i | $net_o | $block_i | $block_o | $pids"
	# store into the table
	mysql --user="root" --password="crash" --database="datexla_dcn" --execute="INSERT INTO docker_stats(container_id, cpu_percent, mem_usage, mem_limit, mem_percent, net_i, net_o, block_i, block_o, pids) VALUES ('$container_id', '$cpu_percent', '$mem_usage', '$mem_limit', '$mem_percent', '$net_i', '$net_o', '$block_i', '$block_o', '$pids')"
done