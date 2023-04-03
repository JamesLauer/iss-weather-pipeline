INSERT INTO {}
	SELECT
		P.city
		, P.lat
		, P.lon
		, P.region
		, P.country
		, W.timezone
        , date_format(at_timezone(from_unixtime(P.startvisibility), W.timezone),'%T') AS start_time
        , date_format(at_timezone(from_unixtime(P.startvisibility), W.timezone),'%Y-%m-%d') AS start_date
		, P.startaz
		, P.startazcompass
		, P.startel
		, P.maxaz
		, P.maxazcompass
		, P.maxel
        , date_format(at_timezone(from_unixtime(P.maxutc), W.timezone),'%T') AS max_time
        , date_format(at_timezone(from_unixtime(P.maxutc), W.timezone),'%Y-%m-%d') AS max_date
		, P.endaz
		, P.endazcompass
        , date_format(at_timezone(from_unixtime(P.endutc), W.timezone),'%T') AS end_time
        , date_format(at_timezone(from_unixtime(P.endutc), W.timezone),'%Y-%m-%d') AS end_date
		, P.mag
		, P.duration
		, W.temp
		, W.feels_like
		, W.pressure
		, W.humidity
		, W.dew_point
		, W.clouds
		, W.visibility
		, W.wind_speed
		, W.wind_deg
		, W.wind_gust
		, W.pop
		, W.main
		, W.description
		, W.rain
		, W.snow
		, W.year
		, W.month
		, W.day
	FROM {} AS P
	INNER JOIN {} AS W
		ON date_format(from_unixtime(P.startutc), '%Y-%m-%d %H')
			= date_format(from_unixtime(W.dt), '%Y-%m-%d %H')
		AND P.city = W.city
		AND P.region= W.region
		AND P.country = W.country
	WHERE W.year = date_format(CURRENT_TIMESTAMP, '%Y')
		AND W.month = date_format(CURRENT_TIMESTAMP, '%m')
		AND W.day = date_format(CURRENT_TIMESTAMP, '%d');
