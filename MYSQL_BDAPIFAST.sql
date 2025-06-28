DROP DATABASE IF EXISTS BDAPIFast;
CREATE DATABASE BDAPIFast;

USE BDAPIFast;

CREATE TABLE producto (
    id VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    pre DOUBLE NOT NULL DEFAULT 0.0,
    rang INT NOT NULL DEFAULT 0,
    Img VARCHAR(255) NOT NULL
);

INSERT INTO producto (id, nom, pre, rang, Img) VALUES
('P001', 'Teclado Mecánico', 59.99, 5, 'https://example.com/teclado.jpg'),
('P002', 'Mouse Gamer', 29.99, 4, 'https://example.com/mouse.jpg'),
('P003', 'Monitor 24"', 199.99, 5, 'https://example.com/monitor.jpg'),
('P004', 'Silla Ergonómica', 129.99, 4, 'https://example.com/silla.jpg'),
('P005', 'Laptop Core i7', 799.99, 5, 'https://example.com/laptop.jpg'),
('P006', 'Auriculares Bluetooth', 49.99, 4, 'https://example.com/auriculares.jpg'),
('P007', 'Disco SSD 1TB', 89.99, 5, 'https://example.com/ssd.jpg'),
('P008', 'Impresora Multifunción', 149.99, 3, 'https://example.com/impresora.jpg'),
('P009', 'Tablet 10"', 299.99, 4, 'https://example.com/tablet.jpg'),
('P010', 'Cámara Web HD', 39.99, 4, 'https://example.com/camara.jpg');

SELECT * FROM producto;

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    contrasena VARCHAR(255) NOT NULL
);

INSERT INTO usuario (nombre_usuario, contrasena) VALUES
('jose', '123'),
('ana', '321'),
('luis789', '123');

SELECT * FROM usuario;


CREATE TABLE facturas (
    cod_fac VARCHAR(20) PRIMARY KEY,
    cod_ped INT,
    id_emp INT,
    fecha_fac DATE,
    hora_fac TIME,
    sub_fac DECIMAL(10,2),
    igv_fac DECIMAL(10,2),
    total_fac DECIMAL(10,2),
    act_fac TINYINT
);

