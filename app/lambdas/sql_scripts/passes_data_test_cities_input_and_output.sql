SELECT COUNT(DISTINCT(city, region))
FROM {}
WHERE day = date_format(current_date, '%d')
    AND month = date_format(current_date, '%m')
    AND year = date_format(current_date, '%Y')
