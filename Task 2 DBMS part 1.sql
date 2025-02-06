create database marketplacedb;

use marketplacedb;

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    vendor_id INT,
    price DECIMAL(10, 2)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(50),
    address TEXT
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    order_date DATE,
    quantity INT,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

#Import the data from csv and verifying with count function
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM customers; 
SELECT COUNT(*) FROM orders; 

# Series of SQL queries
#Only products that appear in the orders table will be included in the result. If a product has never been ordered, it won't show up because the JOIN requires a match between products.product_id and orders.product_id.
SELECT p.product_name, p.price, p.vendor_id
FROM products p
JOIN orders o ON p.product_id = o.product_id;

#Only customers who have placed an order for this product will appear in the results.
SELECT c.customer_name, c.email, o.product_id
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.product_id = 1;

# filtering 
SELECT * FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';

SELECT COUNT(*) AS total_orders
FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';

SELECT COUNT(*) AS total
FROM orders
WHERE quantity > 3;

#Aggregation

 #Maximum and Minimum Order Total by Customer
 SELECT c.customer_name, 
       MAX(o.total_amount) AS max_order_total,
       MIN(o.total_amount) AS min_order_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name;

#Set operation
  #customers ID AND NAME who placed orders in January 2024 and in February 2024
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE c.customer_id IN (
    SELECT customer_id 
    FROM orders
    WHERE MONTH(order_date) = 1 AND YEAR(order_date) = 2024
    UNION
    SELECT customer_id 
    FROM orders
    WHERE MONTH(order_date) = 2 AND YEAR(order_date) = 2024
);

# Window Funtion
   # Ranking Vendors by Total Sales
SELECT p.vendor_id, 
       SUM(o.total_amount) AS total_sales,
       RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS rank1
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.vendor_id;