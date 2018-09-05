-- Schema for aws/dd inventory

create table inventory
(
    id integer primary key autoincrement not null,
    aws_instance_id		varchar(255),
    external_ip			varchar(255),
    internal_ip			varchar(255),
    aws_hostname		varchar(255),
    aws_region			varchar(255),
    reported_by			varchar(255)
);

-- CREATE UNIQUE INDEX IF NOT EXISTS uniquehosts ON inventory (aws_hostname,reported_by);
