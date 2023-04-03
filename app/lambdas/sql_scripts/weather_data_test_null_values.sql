SELECT city, region, dt, COUNT(*) AS containing_nulls
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
        timezone IS NULL OR
        timezone_offset IS NULL OR
        dt IS NULL OR
        temp IS NULL OR
        feels_like IS NULL OR
        pressure IS NULL OR
        humidity IS NULL OR
        dew_point IS NULL OR
        uvi IS NULL OR
        clouds IS NULL OR
        visibility IS NULL OR
        wind_speed IS NULL OR
        wind_deg IS NULL OR
        wind_gust IS NULL OR
        pop IS NULL OR
        id IS NULL OR
        main IS NULL OR
        description IS NULL OR
        icon IS NULL
    )
GROUP BY city, region, dt
LIMIT 3;
