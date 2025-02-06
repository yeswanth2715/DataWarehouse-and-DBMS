## Creating Procedure
DELIMITER //

CREATE PROCEDURE monthly_report(IN report_month VARCHAR(7))
BEGIN
    DECLARE total_revenue DECIMAL(10,2);
    DECLARE assumed_costs DECIMAL(10,2);
    DECLARE profit DECIMAL(10,2);
    DECLARE total_orders INT;

    -- Calculate total revenue for the given month
    SELECT SUM(o.total_amount) INTO total_revenue
    FROM orders o
    WHERE DATE_FORMAT(o.order_date, '%Y-%m') = report_month;

    -- Calculate total number of orders for the given month
    SELECT COUNT(o.order_id) INTO total_orders
    FROM orders o
    WHERE DATE_FORMAT(o.order_date, '%Y-%m') = report_month;

    -- Assume costs as a percentage (e.g., 60%) of total revenue
    SET assumed_costs = total_revenue * 0.6;

    -- Calculate profit
    SET profit = total_revenue - assumed_costs;

    -- Output the report
    SELECT 
        report_month AS Report_Month,
        total_revenue AS Total_Revenue,
        assumed_costs AS Assumed_Costs,
        profit AS Profit,
        total_orders AS Total_Orders;
END //

DELIMITER ;

CALL monthly_report('2024-01');

CREATE TABLE UserPreferences (
    PreferenceID INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    Category VARCHAR(255),
    ViewedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
CREATE TABLE Recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    recommendation_reason VARCHAR(255),
    date_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

DELIMITER $$





CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    INSERT INTO userpreferences (customer_id, product_id, vieweddate)
    VALUES (NEW.customer_id, NEW.product_id, NOW());
END $$

DELIMITER ;


INSERT INTO orders (customer_id, product_id, order_date, quantity)
VALUES (101, 25, '2024-02-06', 2);
SELECT * FROM userpreferences WHERE customer_id = 101;


CREATE EVENT DailyRecommendationUpdate
ON SCHEDULE EVERY 1 DAY
DO 
INSERT INTO recommendations (customer_id, product_id, recommendation_reason, date_generated)
SELECT 
        up.customer_id, 
        p.product_id, 
        'Based on your recent views', 
        NOW()
    FROM userpreferences up
    JOIN products p ON up.product_id != p.product_id
    ORDER BY RAND()
    LIMIT 5;
    
    
INSERT INTO recommendations (customer_id, product_id, recommendation_reason, date_generated)
SELECT 
    up.customer_id, 
    p.product_id, 
    'Based on your recent views', 
    NOW()
FROM userpreferences up
JOIN products p ON up.product_id != p.product_id
ORDER BY RAND()
LIMIT 5;

SELECT * FROM recommendations;






























