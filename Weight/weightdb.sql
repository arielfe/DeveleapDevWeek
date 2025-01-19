CREATE DATABASE IF NOT EXISTS weight;
USE weight;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    datetime DATETIME,
    direction VARCHAR(4),
    truck VARCHAR(50),
    containers TEXT,
    bruto INT,
    truckTara INT,
    neto INT,
    produce VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS containers_registered (
    container_id VARCHAR(50) PRIMARY KEY,
    weight INT,
    unit VARCHAR(3)
);

-- Insert containers (all weights in kg)
INSERT INTO containers_registered (container_id, weight, unit) VALUES
('C1', 100, 'kg'),
('C2', 150, 'kg'),
('C3', 200, 'kg'),
('C4', 250, 'kg'),
('C5', 300, 'kg'),
('C6', 175, 'kg'),
('C7', 225, 'kg'),
('C8', 275, 'kg'),
('C9', 325, 'kg'),
('C10', 280, 'kg'),
('C11', 190, 'kg'),
('C12', 220, 'kg'),
('C13', 170, 'kg'),
('C14', 210, 'kg'),
('C15', 240, 'kg');

-- Insert sample transactions covering various scenarios (all weights in kg)
INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce) VALUES
-- Regular in-out cycle with single container
('2024-01-15 08:00:00', 'in', 'T1', 'C1', 4500, NULL, NULL, 'tomatoes'),
('2024-01-15 09:30:00', 'out', 'T1', 'C1', 4500, 2000, 2400, 'tomatoes'),

-- Multiple containers per truck
('2024-01-15 10:00:00', 'in', 'T2', 'C2,C3', 6000, NULL, NULL, 'potatoes'),
('2024-01-15 11:45:00', 'out', 'T2', 'C2,C3', 6000, 2200, 3450, 'potatoes'),

-- Heavy load with three containers
('2024-01-15 13:00:00', 'in', 'T3', 'C4,C5,C6', 7500, NULL, NULL, 'watermelons'),
('2024-01-15 14:30:00', 'out', 'T3', 'C4,C5,C6', 7500, 2500, 4275, 'watermelons'),

-- Standalone container weighing
('2024-01-15 15:00:00', 'none', NULL, 'C7', 500, NULL, 275, 'oranges'),
('2024-01-15 15:30:00', 'none', NULL, 'C8,C9', 800, NULL, 200, 'apples'),

-- Multiple trucks same day
('2024-01-16 08:00:00', 'in', 'T4', 'C10', 5200, NULL, NULL, 'cucumbers'),
('2024-01-16 08:15:00', 'in', 'T5', 'C11', 4800, NULL, NULL, 'carrots'),
('2024-01-16 09:45:00', 'out', 'T4', 'C10', 5200, 2100, 2820, 'cucumbers'),
('2024-01-16 10:00:00', 'out', 'T5', 'C11', 4800, 2000, 2610, 'carrots'),

-- Late day transactions
('2024-01-16 16:00:00', 'in', 'T6', 'C12,C13', 6500, NULL, NULL, 'onions'),
('2024-01-16 17:30:00', 'out', 'T6', 'C12,C13', 6500, 2300, 3810, 'onions'),

-- Weekend transactions
('2024-01-17 09:00:00', 'in', 'T7', 'C14,C15', 7000, NULL, NULL, 'lettuce'),
('2024-01-17 10:30:00', 'out', 'T7', 'C14,C15', 7000, 2400, 4150, 'lettuce'),

-- Different produce types
('2024-01-17 11:00:00', 'in', 'T8', 'C1,C2', 5500, NULL, NULL, 'cabbage'),
('2024-01-17 12:30:00', 'out', 'T8', 'C1,C2', 5500, 2100, 3150, 'cabbage'),

-- Multiple containers
('2024-01-17 13:00:00', 'in', 'T9', 'C4,C8,C12', 6800, NULL, NULL, 'peppers'),
('2024-01-17 14:45:00', 'out', 'T9', 'C4,C8,C12', 6800, 2200, 3855, 'peppers'),

-- Recent transactions
('2024-01-18 08:00:00', 'in', 'T10', 'C3,C6', 5800, NULL, NULL, 'eggplants'),
('2024-01-18 09:30:00', 'out', 'T10', 'C3,C6', 5800, 2000, 3425, 'eggplants'),

-- Standalone container weighings with multiple containers
('2024-01-18 10:00:00', 'none', NULL, 'C7,C9,C11', 1200, NULL, 460, 'grapes'),
('2024-01-18 10:30:00', 'none', NULL, 'C13,C15', 900, NULL, 490, 'berries'),

-- Latest transactions
('2024-01-19 08:00:00', 'in', 'T11', 'C2,C4,C6', 6200, NULL, NULL, 'melons'),
('2024-01-19 09:45:00', 'out', 'T11', 'C2,C4,C6', 6200, 2300, 3325, 'melons');