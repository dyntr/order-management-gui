-- copyright -> Patrick Dyntr, C4b // **Škola**: Střední průmyslová škola elektrotechnická, Praha 2, Ječná 30

CREATE DATABASE IF NOT EXISTS PVDB;
USE PVDB;

DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Users;

CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Email VARCHAR(100),
    IsActive ENUM('Aktivní','Neaktivní','Pozastaveno') DEFAULT 'Aktivní',
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Categories (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Products (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    ProductName VARCHAR(100) NOT NULL,
    Price FLOAT NOT NULL,
    Stock INT DEFAULT 0,
    CategoryID INT NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    TotalAmount FLOAT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS OrderDetails (
    OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    PricePerUnit FLOAT NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE
);

CREATE OR REPLACE VIEW OrderSummary AS
SELECT
  o.OrderID,
  o.OrderDate,
  u.Username,
  IFNULL(SUM(d.Quantity*d.PricePerUnit),0) AS TotalValue
FROM Orders o
JOIN Users u ON o.UserID = u.UserID
LEFT JOIN OrderDetails d ON o.OrderID = d.OrderID
GROUP BY o.OrderID;

-- copyright -> Patrick Dyntr, C4b // **Škola**: Střední průmyslová škola elektrotechnická, Praha 2, Ječná 30