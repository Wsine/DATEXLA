-- user:root passwd:crash

-- create a new dateabas
DROP DATABASE IF EXISTS datexla_dcn;
CREATE DATABASE datexla_dcn default character set=utf8;

USE datexla_dcn;

-- create a new table
DROP TABLE IF EXISTS cluster_stats;
CREATE TABLE cluster_stats(
    id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'auto increment id',
    node_id varchar(30) NOT NULL UNIQUE COMMENT 'node id',
    score double(8, 3) NOT NULL COMMENT 'score',
    cpu_score double(8, 3) NOT NULL COMMENT 'cpu score',
    mem_score double(8, 3) NOT NULL COMMENT 'memory score'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='docker stats';
