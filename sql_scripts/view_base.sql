SELECT t1.login, t1.password, t2.attempts_count, t1.created_at, t2.last_attempt
FROM users t1
LEFT JOIN attempts t2
ON t1.id = t2.user_id