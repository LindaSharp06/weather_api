-- Export request history and received data (JOIN of requests and responses).
-- Tables: requests (id, timestamp), responses (id, request_id FK, exchange_rate, status_code)

SELECT
    r.id          AS request_id,
    r.timestamp   AS request_time,
    res.id        AS response_id,
    res.exchange_rate,
    res.status_code
FROM requests r
JOIN responses res ON res.request_id = r.id
ORDER BY r.id DESC;
