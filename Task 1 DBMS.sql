create database DWstore;

USE DWstore;
-- Step 1: Create Products Table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY,
    ProductName VARCHAR(100) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    VendorID INT NOT NULL,
    Revenue DECIMAL(10,2) NOT NULL
);

-- Step 2: Create Orders Table
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT NOT NULL,
    TimeSpent INT NOT NULL,
    OrderStatus VARCHAR(20) NOT NULL,
    ComplaintID INT,
    VendorID INT NOT NULL -- Added VendorID to link Orders with Vendors
);

-- Step 3: Create Vendors Table 
CREATE TABLE Vendors (
    VendorID INT PRIMARY KEY,
    VendorName VARCHAR(100) NOT NULL,
    VendorContact VARCHAR(50) NOT NULL,
    VendorRating DECIMAL(3,2), -- Added VendorRating column
    VendorAddress VARCHAR(255) -- Added VendorAddress column
);

-- Step 4: Create Complaints Table 
CREATE TABLE Complaints (
    ComplaintID INT PRIMARY KEY,
    OrderID INT NOT NULL,
    Reason VARCHAR(255) NOT NULL,
    ResolutionStatus VARCHAR(50)
);

#Add Foreign Keys
ALTER TABLE Products
ADD CONSTRAINT FK_Products_Vendors
FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID);

ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Complaints
FOREIGN KEY (ComplaintID) REFERENCES Complaints(ComplaintID);

ALTER TABLE Complaints
ADD CONSTRAINT FK_Complaints_Orders
FOREIGN KEY (OrderID) REFERENCES Orders(OrderID);

-- Step 6: Insert Data into Vendors Table
INSERT INTO Vendors (VendorID, VendorName, VendorContact, VendorRating, VendorAddress) VALUES
(101, 'TechCorp', 'techcorp@example.com', 4.5, '123 Tech Street, Berlin'),
(102, 'Sportify', 'sportify@example.com', 4.2, '456 Sport Lane, Berlin'),
(103, 'AccessoryHub', 'accessoryhub@example.com', 4.7, '789 Accessory Ave, Berlin'),
(104, 'HomeDecor', 'homedecor@example.com', 4.0, '321 Home Road, Berlin'),
(105, 'FashionWorld', 'fashionworld@example.com', 3.8, '654 Fashion Blvd, Berlin');

-- Step 7: Insert Data into Products Table
INSERT INTO Products (ProductID, ProductName, Category, VendorID, Revenue) VALUES
(1, 'Phone Case', 'Electronics', 101, 5000.50),
(2, 'Running Shoes', 'Sportswear', 102, 12000.00),
(3, 'Wireless Mouse', 'Electronics', 101, 3000.25),
(4, 'Backpack', 'Accessories', 103, 8000.00),
(5, 'Desk Lamp', 'Home Decor', 104, 1500.75),
(6, 'Sunglasses', 'Accessories', 105, 950.00),
(7, 'Yoga Mat', 'Sportswear', 102, 7800.30),
(8, 'Coffee Maker', 'Home Decor', 104, 5000.00),
(9, 'Earbuds', 'Electronics', 101, 6000.00),
(10, 'Bicycle', 'Sportswear', 102, 25000.00);

-- Step 8: Insert Data into Orders Table
INSERT INTO Orders (OrderID, CustomerID, TimeSpent, OrderStatus, ComplaintID, VendorID) VALUES
(1001, 201, 15, 'Complete', NULL, 101),
(1002, 202, 25, 'Complete', NULL, 102),
(1003, 203, 30, 'Pending', NULL, 103),
(1004, 204, 20, 'Complete', 5001, 104),
(1005, 205, 40, 'Pending', 5002, 105),
(1006, 206, 50, 'Complete', NULL, 101),
(1007, 207, 60, 'Pending', NULL, 102),
(1008, 208, 45, 'Complete', NULL, 103),
(1009, 209, 10, 'Cancelled', 5003, 104),
(1010, 210, 35, 'Complete', NULL, 105);

-- Insert Data into Complaints Table
INSERT INTO Complaints (ComplaintID, OrderID, Reason, ResolutionStatus) VALUES
(5001, 1004, 'Damaged product', 'Resolved'),
(5002, 1005, 'Late delivery', 'Pending'),
(5003, 1009, 'Incorrect item', 'Resolved');

###Normalisation
ALTER TABLE Orders
DROP COLUMN VendorID;
CREATE TABLE OrderDetails ( 
    OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    VendorID INT NOT NULL,
    Quantity INT NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID)
);
INSERT INTO OrderDetails (OrderID, ProductID, VendorID, Quantity)
VALUES
(1005, 5, 105, 1),
(1010, 2, 105, 2),
(1004, 4, 104, 3),
(1009, 8, 104, 1),
(1003, 7, 103, 1),
(1008, 9, 103, 1),
(1002, 3, 102, 2),
(1007, 1, 102, 1),
(1001, 6, 101, 1),
(1006, 10, 101, 2);


CREATE TABLE ComplaintReasons (
    ReasonID INT PRIMARY KEY,
    Reason VARCHAR(255) NOT NULL
);

CREATE TABLE ResolutionStatus (
    ResolutionID INT PRIMARY KEY,
    ResolutionStatus VARCHAR(50) NOT NULL
);

INSERT INTO ComplaintReasons (ReasonID, Reason) VALUES
(1, 'Damaged product'),
(2, 'Late delivery'),
(3, 'Incorrect item');

INSERT INTO ResolutionStatus (ResolutionID, ResolutionStatus) VALUES
(1, 'Resolved'),
(2, 'Pending');

ALTER TABLE Complaints
ADD CONSTRAINT FK_Complaints_ReasonID
FOREIGN KEY (ReasonID) REFERENCES ComplaintReasons(ReasonID);

ALTER TABLE Complaints
ADD CONSTRAINT FK_Complaints_ResolutionID
FOREIGN KEY (ResolutionID) REFERENCES ResolutionStatus(ResolutionID);

-- Update rows with Reason and Resolution
UPDATE Complaints
SET ReasonID = 1, ResolutionID = 1
WHERE ComplaintID = 5001;

UPDATE Complaints
SET ReasonID = 2, ResolutionID = 2
WHERE ComplaintID = 5002;

UPDATE Complaints
SET ReasonID = 3, ResolutionID = 1
WHERE ComplaintID = 5003;

-- Index on ProductID for faster lookups in Orders and OrderDetails tables
CREATE INDEX idx_product_id ON Products (ProductID);

-- Index on VendorID for optimizing vendor-related queries
CREATE INDEX idx_vendor_id ON Vendors (VendorID);

-- Index on CustomerID for improving order retrieval performance
CREATE INDEX idx_customer_id ON Orders (CustomerID);

-- Index on OrderID for faster order lookups and JOINs
CREATE INDEX idx_order_id ON Orders (OrderID);
CREATE INDEX idx_order_id_details ON OrderDetails (OrderID);

-- Index on ComplaintID for optimizing complaint resolution queries
CREATE INDEX idx_complaint_id ON Complaints (ComplaintID);

-- Index on OrderDate for performance improvements in date range filtering
CREATE INDEX idx_order_date ON Orders (OrderStatus);


###
#code for top selling items
SELECT p.ProductName, SUM(od.Quantity) AS TotalQuantity
FROM orderdetails od
JOIN products p ON od.ProductID = p.ProductID
GROUP BY p.ProductName
ORDER BY TotalQuantity DESC;

#Vendors recieving most complaints
SELECT v.VendorName, COUNT(c.ComplaintID) AS TotalComplaints
FROM complaints c
JOIN orders o ON c.OrderID = o.OrderID
JOIN orderdetails od ON o.OrderID = od.OrderID
JOIN vendors v ON od.VendorID = v.VendorID
GROUP BY v.VendorName
ORDER BY TotalComplaints DESC;

# Revenue by Vendor
SELECT v.VendorName,SUM(od.Quantity * p.Revenue) AS TotalRevenue
FROM orderdetails od
JOIN vendors v ON od.VendorID = v.VendorID
JOIN products p ON od.ProductID = p.ProductID
GROUP BY v.VendorName
ORDER BY TotalRevenue DESC;


## Trigger ##
DELIMITER //

CREATE TRIGGER UpdateResolutionID
BEFORE UPDATE ON Complaints
FOR EACH ROW
BEGIN
    -- Automatically update ResolutionID when the status changes
    IF NEW.ResolutionID IS NOT NULL THEN
        SET NEW.ResolutionID = (
            SELECT ResolutionID 
            FROM ResolutionStatus 
            WHERE ResolutionID = NEW.ResolutionID
        );
    END IF;
END;
//

DELIMITER ;






