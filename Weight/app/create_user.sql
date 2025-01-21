-- Drop user if exists and recreate
DROP USER IF EXISTS 'user_weight'@'%';
CREATE USER 'user_weight'@'%' IDENTIFIED BY 'bashisthebest';
GRANT ALL PRIVILEGES ON weight.* TO 'user_weight'@'%';
FLUSH PRIVILEGES;
