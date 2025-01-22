-- Drop database if exists and create new one
DROP DATABASE IF EXISTS `weight`;
CREATE DATABASE IF NOT EXISTS `weight`;
USE weight;

-- Create containers_registered table
CREATE TABLE IF NOT EXISTS `containers_registered` (
  `container_id` varchar(15) NOT NULL,
  `weight` int(12) DEFAULT NULL,
  `unit` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`container_id`)
) ENGINE=MyISAM;

-- Create transactions table
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL,
  `direction` varchar(10) DEFAULT NULL,
  `truck` varchar(50) DEFAULT NULL,
  `containers` varchar(10000) DEFAULT NULL,
  `bruto` int(12) DEFAULT NULL,
  `truckTara` int(12) DEFAULT NULL,
  `neto` int(12) DEFAULT NULL,
  `produce` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001;

-- Insert container registration data
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES 
('C1001', 1000, 'kg'),
('C1002', 2500, 'lbs'),
('C1003', 750, 'kg'),
('C1004', 1800, 'lbs'),
('C1005', 900, 'kg'),
('C1006', 2200, 'lbs'),
('C1007', 850, 'kg'),
('C1008', 1950, 'lbs'),
('C1009', 1100, 'kg'),
('C1010', 2100, 'lbs');

-- Insert transactions data

-- January 15th transactions
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-15 08:00:00', 'in', 'T1001', 'C1001,C1002', 15000, NULL, NULL, 'tomatoes'),
('2024-01-15 16:00:00', 'out', 'T1001', 'C1001,C1002', 15000, 8000, 5000, 'tomatoes'),
('2024-01-15 09:30:00', 'in', 'T1002', 'C1003', 12000, NULL, NULL, 'cucumbers'),
('2024-01-15 17:30:00', 'out', 'T1002', 'C1003', 12000, 7500, 3750, 'cucumbers');

-- January 16th transactions
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-16 08:15:00', 'in', 'T1003', 'C1004,C1005', 16000, NULL, NULL, 'potatoes'),
('2024-01-16 16:15:00', 'out', 'T1003', 'C1004,C1005', 16000, 8500, 6600, 'potatoes'),
('2024-01-16 10:30:00', 'none', NULL, 'C1006', 2500, NULL, 700, 'onions');

-- January 17th transactions (including unknown container)
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-17 09:00:00', 'in', 'T1004', 'C9999', 13000, NULL, NULL, 'carrots'),
('2024-01-17 17:00:00', 'out', 'T1004', 'C9999', 13000, 7000, NULL, 'carrots'),
('2024-01-17 11:30:00', 'none', NULL, 'C1007,C1008', 3000, NULL, 1450, 'lettuce');

-- January 18th transactions
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-18 08:30:00', 'in', 'T1005', 'C1001,C1002,C1003', 20000, NULL, NULL, 'cabbage'),
('2024-01-18 15:30:00', 'out', 'T1005', 'C1001,C1002,C1003', 20000, 9000, 8350, 'cabbage');

-- January 19th transactions
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-19 09:15:00', 'in', 'T1006', 'C1009,C1010', 17500, NULL, NULL, 'beets'),
('2024-01-19 16:45:00', 'out', 'T1006', 'C1009,C1010', 17500, 8800, 7600, 'beets');

-- January 20th transactions (pending in)
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-20 08:45:00', 'in', 'T1007', 'C1001,C1004', 14500, NULL, NULL, 'peppers'),
('2024-01-20 10:30:00', 'none', NULL, 'C1002', 2800, NULL, 1300, 'eggplants');

-- January 21st transactions (current date in system)
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-21 09:00:00', 'in', 'T1008', 'C1005,C1006', 16800, NULL, NULL, 'zucchini'),
('2024-01-21 10:15:00', 'none', NULL, 'C1003,C1007', 2900, NULL, 1300, 'radishes');

-- Additional edge cases
INSERT INTO `transactions` 
(`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES
('2024-01-21 11:00:00', 'in', 'T1009', 'C8888,C9999', 15000, NULL, NULL, 'celery'),
('2024-01-21 11:30:00', 'none', NULL, 'C7777', 2000, NULL, NULL, 'corn');
