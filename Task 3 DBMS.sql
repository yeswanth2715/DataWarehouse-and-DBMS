# Optimising the Query and Performance
Use marketplacedb;

##Customer Purchase Report for 2024
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
JOIN Products p ON o.product_id = p.product_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;


###did profile for the complex query
SET profiling = 1;
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
JOIN Products p ON o.product_id = p.product_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;
 

SHOW PROFILE FOR QUERY 1;
SET profiling = 0;

### and then looked for profiling  with explain function
explain
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
JOIN Products p ON o.product_id = p.product_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;

###Indexing
CREATE INDEX idx_order_date ON Orders(order_date);
CREATE INDEX idx_customer_date ON Orders(customer_id, order_date);


##Query Restructing
WITH Filtered_Orders AS (
    SELECT * 
    FROM Orders
    WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
)
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Filtered_Orders o
JOIN Customers c ON c.customer_id = o.customer_id
JOIN Products p ON p.product_id = o.product_id
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;

EXPLAIN
WITH Filtered_Orders AS (
    SELECT *
    FROM Orders
    WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
)
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Filtered_Orders o
JOIN Customers c ON c.customer_id = o.customer_id
JOIN Products p ON p.product_id = o.product_id
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;



WITH Filtered_Orders AS (
    SELECT *
    FROM Orders FORCE INDEX (idx_order_date) -- or use idx_orders_date_customer
    WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
)
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Filtered_Orders o
JOIN Customers c ON c.customer_id = o.customer_id
JOIN Products p ON p.product_id = o.product_id
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;

##after doing above step still got not optmisied so i did Force Index Usage
# WHERE condition (order_date BETWEEN '2024-01-01' AND '2024-12-31), instead of scanning the entire table.his leads to improved query performance as fewer rows are processed during filtering and subsequent operations like JOINs and aggregations.
explain
WITH Filtered_Orders AS (
    SELECT *
    FROM Orders FORCE INDEX (idx_order_date) -- or use idx_orders_date_customer
    WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
)
SELECT 
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    SUM(o.total_amount) AS total_spent,
    COUNT(o.order_id) AS total_orders
FROM Filtered_Orders o
JOIN Customers c ON c.customer_id = o.customer_id
JOIN Products p ON p.product_id = o.product_id
GROUP BY c.customer_id, c.customer_name, p.product_id, p.product_name
ORDER BY c.customer_id;




