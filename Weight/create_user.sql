-- Drop user if exists and recreate
DROP USER IF EXISTS 'nati'@'%';
CREATE USER 'nati'@'%' IDENTIFIED BY 'bashisthebest';
GRANT ALL PRIVILEGES ON weight.* TO 'nati'@'%';
FLUSH PRIVILEGES;