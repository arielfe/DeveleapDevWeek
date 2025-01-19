DROP DATABASE IF EXISTS weight;
CREATE DATABASE weight;
USE weight;

-- Create user and grant privileges
DROP USER IF EXISTS 'nati'@'%';
CREATE USER 'nati'@'%' IDENTIFIED BY 'bashisthebest';
GRANT ALL PRIVILEGES ON weight.* TO 'nati'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Create tables
CREATE TABLE containers_registered (
  container_id varchar(15) NOT NULL,
  weight int(12) DEFAULT NULL,
  unit varchar(10) DEFAULT NULL,
  PRIMARY KEY (container_id)
) ENGINE=MyISAM;

CREATE TABLE transactions (
  id int(12) NOT NULL AUTO_INCREMENT,
  datetime datetime DEFAULT NULL,
  direction varchar(10) DEFAULT NULL,
  truck varchar(50) DEFAULT NULL,
  containers varchar(10000) DEFAULT NULL,
  bruto int(12) DEFAULT NULL,
  truckTara int(12) DEFAULT NULL,
  neto int(12) DEFAULT NULL,
  produce varchar(50) DEFAULT NULL,
  session_id int(12) DEFAULT NULL,
  weight INT(12) DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=MyISAM AUTO_INCREMENT=10001;

-- Insert containers data
INSERT INTO containers_registered (container_id, weight, unit)
VALUES 
  ('1000', 14340, 'kg'),
  ('1001', 8590, 'lbs'),
  ('1002', 6776, 'lbs'),
  ('1003', 17099, 'lbs'),
  ('1004', 15311, 'lbs'),
  ('1005', 6801, 'lbs'),
  ('1006', 8991, 'lbs'),
  ('1007', 10016, 'lbs'),
  ('1008', 14003, 'lbs'),
  ('1009', 5010, 'lbs'),
  ('1010', 7796, 'kg'),
  ('1011', 18805, 'kg'),
  ('1012', 3836, 'lbs'),
  ('1013', 10911, 'kg'),
  ('1014', 10036, 'lbs'),
  ('1015', 16807, 'lbs'),
  ('1016', 9929, 'kg'),
  ('1017', 13977, 'lbs'),
  ('1018', 5994, 'kg'),
  ('1019', 4945, 'lbs');

-- Insert transactions data
INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id)
VALUES 
  ('2025-01-19 15:53:17', 'none', '1000', '1000', 17396, 4316, 13080, 'na', 3533),
  ('2025-01-19 15:58:17', 'none', '1001', '1001', 11834, 3840, 7994, 'apple', 7106),
  ('2025-01-19 16:03:17', 'in', '1002', '1002,1002', 7633, 6791, 842, 'orange', 7371),
  ('2025-01-19 16:08:17', 'in', '1003', '1003', 21077, 4178, 16899, 'tomato', 8991),
  ('2025-01-19 16:13:17', 'none', '1004', '1004', 19709, 4055, 15654, 'tomato', 7578),
  ('2025-01-19 16:18:17', 'out', '1000', '1005,1005', 7969, 6379, 1590, 'na', 1059),
  ('2025-01-19 16:23:17', 'out', '1001', '1006', 11302, 6993, 4309, 'na', 3158),
  ('2025-01-19 16:28:17', 'in', '1002', '1007', 12979, 6405, 6574, 'orange', 2345),
  ('2025-01-19 16:33:17', 'none', '1003', '1008', 17981, 4513, 13468, 'tomato', 7167),
  ('2025-01-19 16:38:17', 'none', '1004', '1009', 5981, 5634, 347, 'apple', 9962),
  ('2025-01-19 16:43:17', 'out', '1000', '1010', 9778, 5614, 4164, 'tomato', 1231),
  ('2025-01-19 16:48:17', 'none', '1001', '1011,1011,1011', 22779, 3206, 19573, 'na', 1856),
  ('2025-01-19 16:53:17', 'out', '1002', '1012,1012', 6192, 4749, 1443, 'apple', 8486),
  ('2025-01-19 16:58:17', 'in', '1003', '1013,1013,1013', 11705, 3302, 8403, 'apple', 6121),
  ('2025-01-19 17:03:17', 'in', '1004', '1014', 13634, 3641, 9993, 'apple', 6772),
  ('2025-01-19 17:08:17', 'none', '1000', '1015', 19560, 4400, 15160, 'na', 3518),
  ('2025-01-19 17:13:17', 'in', '1001', '1016,1016,1016', 14908, 4238, 10670, 'tomato', 4932),
  ('2025-01-19 17:18:17', 'in', '1002', '1017,1017', 16611, 3736, 12875, 'tomato', 8720),
  ('2025-01-19 17:23:17', 'in', '1003', '1018,1018,1018', 7220, 3021, 4199, 'orange', 1485),
  ('2025-01-19 17:28:17', 'out', '1004', '1019,1019', 6179, 2839, 3340, 'orange', 2630);