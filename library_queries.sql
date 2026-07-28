-- ============================================================
-- library_queries.sql
-- Analytical SQL queries against the library management database
-- Demonstrates: joins, aggregation, subqueries, date logic, CTEs
-- ============================================================

-- 1. Most borrowed books of all time (top 10)
SELECT
    b.title,
    a.name AS author,
    COUNT(l.loan_id) AS times_borrowed
FROM loans l
JOIN books b ON l.book_id = b.book_id
JOIN authors a ON b.author_id = a.author_id
GROUP BY b.book_id
ORDER BY times_borrowed DESC
LIMIT 10;


-- 2. Currently overdue loans (not yet returned, past due date)
SELECT
    m.name AS member_name,
    b.title,
    l.loan_date,
    l.due_date,
    CAST(julianday('2026-07-28') - julianday(l.due_date) AS INTEGER) AS days_overdue
FROM loans l
JOIN members m ON l.member_id = m.member_id
JOIN books b ON l.book_id = b.book_id
WHERE l.return_date IS NULL
  AND l.due_date < '2026-07-28'
ORDER BY days_overdue DESC;


-- 3. Monthly loan volume trend (seasonality check)
SELECT
    strftime('%Y-%m', loan_date) AS month,
    COUNT(*) AS total_loans
FROM loans
GROUP BY month
ORDER BY month;


-- 4. Genre popularity — total loans and unique borrowers per genre
SELECT
    b.genre,
    COUNT(l.loan_id) AS total_loans,
    COUNT(DISTINCT l.member_id) AS unique_borrowers
FROM loans l
JOIN books b ON l.book_id = b.book_id
GROUP BY b.genre
ORDER BY total_loans DESC;


-- 5. Members with the most overdue returns (a "follow-up needed" list)
-- Uses a subquery to first compute lateness per loan, then aggregates by member.
SELECT
    member_name,
    COUNT(*) AS late_returns
FROM (
    SELECT
        m.name AS member_name,
        l.loan_id,
        julianday(l.return_date) - julianday(l.due_date) AS days_late
    FROM loans l
    JOIN members m ON l.member_id = m.member_id
    WHERE l.return_date IS NOT NULL
      AND julianday(l.return_date) > julianday(l.due_date)
) late_loans
GROUP BY member_name
HAVING late_returns >= 2
ORDER BY late_returns DESC;


-- 6. Book utilization — loans per copy owned (identifies under/over-stocked titles)
SELECT
    b.title,
    b.copies_owned,
    COUNT(l.loan_id) AS total_loans,
    ROUND(CAST(COUNT(l.loan_id) AS FLOAT) / b.copies_owned, 2) AS loans_per_copy
FROM books b
LEFT JOIN loans l ON b.book_id = l.book_id
GROUP BY b.book_id
ORDER BY loans_per_copy DESC;


-- 7. New members by month, and whether they've borrowed anything yet
-- (a CTE identifies each member's first loan date, if any)
WITH first_loans AS (
    SELECT member_id, MIN(loan_date) AS first_loan_date
    FROM loans
    GROUP BY member_id
)
SELECT
    strftime('%Y-%m', m.join_date) AS join_month,
    COUNT(*) AS members_joined,
    SUM(CASE WHEN fl.member_id IS NOT NULL THEN 1 ELSE 0 END) AS members_who_borrowed
FROM members m
LEFT JOIN first_loans fl ON m.member_id = fl.member_id
GROUP BY join_month
ORDER BY join_month;


-- 8. Average loan duration (days) by membership type
SELECT
    m.membership_type,
    ROUND(AVG(julianday(l.return_date) - julianday(l.loan_date)), 1) AS avg_days_held
FROM loans l
JOIN members m ON l.member_id = m.member_id
WHERE l.return_date IS NOT NULL
GROUP BY m.membership_type
ORDER BY avg_days_held DESC;
