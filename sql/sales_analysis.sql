USE retail_analysis;

-- 1. Total sales amount
SELECT ROUND(SUM(SalesAmount), 2) AS TotalSales
FROM salessales;


-- 2. Top 10 countries by total sales
SELECT
    Country,
    ROUND(SUM(SalesAmount), 2) AS TotalSales
FROM salessales
GROUP BY Country
ORDER BY TotalSales DESC
LIMIT 10;


-- 3. Top 10 products by total sales
-- Exclude postage and manual entries
SELECT
    StockCode,
    ROUND(SUM(SalesAmount), 2) AS TotalSales
FROM salessales
WHERE StockCode NOT IN ('DOT', 'POST', 'M')
GROUP BY StockCode
ORDER BY TotalSales DESC
LIMIT 10;


-- 4. Monthly sales from oldest to newest
SELECT
    YEAR(InvoiceDate) AS SalesYear,
    MONTH(InvoiceDate) AS SalesMonth,
    ROUND(SUM(SalesAmount), 2) AS TotalSales
FROM salessales
GROUP BY YEAR(InvoiceDate), MONTH(InvoiceDate)
ORDER BY SalesYear, SalesMonth;


-- 5. Top 10 customers by total sales
SELECT
    CustomerID,
    ROUND(SUM(SalesAmount), 2) AS TotalSales
FROM salessales
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID
ORDER BY TotalSales DESC
LIMIT 10;