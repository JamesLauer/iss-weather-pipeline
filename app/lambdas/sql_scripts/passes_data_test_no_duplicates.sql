SELECT city, region, startutc, COUNT(*) AS duplicates
FROM {}
WHERE day = date_format(current_date, '%d')
    AND month = date_format(current_date, '%m')
    AND year = date_format(current_date, '%Y')
GROUP BY city, region, startutc
HAVING COUNT(*) > 1
