CREATE TABLE history (
    order_id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    person_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    time TEXT NOT NULL,

    FOREIGN KEY (person_id) REFERENCES users(id)
);


SELECT * FROM (SELECT symbol, SUM(shares) AS shares from history WHERE person_id = "3" GROUP BY symbol ORDER BY symbol) WHERE shares > 0;

