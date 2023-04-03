SELECT city, region, startutc, COUNT(*) AS containing_nulls
FROM {}
WHERE
    day = date_format(current_date, '%d')
    AND month = date_format(current_date, '%m')
    AND year = date_format(current_date, '%Y')
    AND (
        city IS NULL OR
        lat IS NULL OR
        lon IS NULL OR
        region IS NULL OR
        country IS NULL OR
        satid IS NULL OR
        satname IS NULL OR
        transactionscount IS NULL
    )
GROUP BY city, region, startutc
