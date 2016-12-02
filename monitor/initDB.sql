-- user:root passwd:crash

-- create a new dateabas
DROP DATABASE IF EXISTS datexla_dcn;
CREATE DATABASE datexla_dcn default character set=utf8;

USE datexla_dcn;

-- create a new table
DROP TABLE IF EXISTS docker_stats;
CREATE TABLE docker_stats (
    id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'auto increment id',
    container_id varchar(20) NOT NULL UNIQUE COMMENT 'container id',
    cpu_percent double(8, 3) NOT NULL COMMENT 'cpu percent',
    mem_usage varchar(20) NOT NULL COMMENT 'memory usage',
    mem_limit varchar(20) NOT NULL COMMENT 'memory limit',
    mem_percent double(8, 3) NOT NULL COMMENT 'memory percent',
    net_i varchar(20) NOT NULL COMMENT 'network input',
    net_o varchar(20) NOT NULL COMMENT 'network output',
    block_i varchar(20) NOT NULL COMMENT 'file block input',
    block_o varchar(20) NOT NULL COMMENT 'file block output',
    pids int(11) NOT NULL COMMENT 'pids'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='docker stats';
