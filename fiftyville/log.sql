-- Keep a log of any SQL queries you execute as you solve the mystery.

-- Get schemata
.schema;

-- Get information about crime_scene_reports table
SELECT * FROM crime_scene_reports LIMIT 10;

-- Ger the report of the theft
SELECT id, description FROM crime_scene_reports WHERE year = 2021 AND month = 7 AND day = 28 AND street = 'Humphrey Street';
-- id 295, time 10:15 at backery, 3 witnesses present

-- interwies with witnesses
SELECT * FROM interviews WHERE year = 2021 AND month = 7 AND day = 28;
-- id's are 161-163

-- To better read
SELECT name, transcript FROM interviews WHERE id > 160 AND id < 164;
-- Ruth: Within 10 minutes thief got into a car in the backery parking lot
-- Eugene: Thief someone recognised. Thief withdrew money earlier at ATM on Leggett Street
--Raymond: Called someone for less than one minute. Panned to take the earliest flight out tomorrow. Accomplice purchased the plane ticket.

-- | Sometime within ten minutes of the theft, I saw the thief get into a car in the bakery parking lot and drive away.
--   If you have security footage from the bakery parking lot, you might want to look for cars that left the parking lot in that time frame.|

-- | I don't know the thief's name, but it was someone I recognized. Earlier this morning, before I arrived at Emma's bakery, I was walking by the ATM on Leggett Street and saw the thief there withdrawing some money.|

-- | As the thief was leaving the bakery, they called someone who talked to them for less than a minute. In the call, I heard the thief say that they were planning to take the earliest flight out of Fiftyville tomorrow.
--   The thief then asked the person on the other end of the phone to purchase the flight ticket.|



-- backery security logs of car
SELECT license_plate FROM bakery_security_logs WHERE year = 2021 AND month = 7 AND day = 28 AND hour = 10 AND minute > 15 AND minute < 25 AND activity = 'exit';
-- Possible escape cars :
-- | 5P2BI95       |
-- | 94KL13X       |
-- | 6P58WS2       |
-- | 4328GD8       |
-- | G412CB7       |
-- | L93JTIZ       |
-- | 322W7JE       |
-- | 0NTHK55       |

-- ATM transactions
SELECT account_number, amount FROM atm_transactions WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw';
-- | account_number | amount |
-- +----------------+--------+
-- | 28500762       | 48     |
-- | 28296815       | 20     |
-- | 76054385       | 60     |
-- | 49610011       | 50     |
-- | 16153065       | 80     |
-- | 25506511       | 20     |
-- | 81061156       | 30     |
-- | 26013199       | 35     |

--Corresponding person id's
SELECT person_id
FROM bank_accounts
WHERE account_number IN (SELECT account_number FROM atm_transactions WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw');

-- | person_id |
-- +-----------+
-- | 686048    |
-- | 514354    |
-- | 458378    |
-- | 395717    |
-- | 396669    |
-- | 467400    |
-- | 449774    |
-- | 438727    |

-- Investigate the call
SELECT caller, receiver FROM phone_calls WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60;
-- |     caller     |    receiver    |
-- +----------------+----------------+
-- | (130) 555-0289 | (996) 555-8899 |
-- | (499) 555-9472 | (892) 555-8872 |
-- | (367) 555-5533 | (375) 555-8161 |
-- | (499) 555-9472 | (717) 555-1342 |
-- | (286) 555-6063 | (676) 555-6554 |
-- | (770) 555-1861 | (725) 555-3243 |
-- | (031) 555-6622 | (910) 555-3251 |
-- | (826) 555-1652 | (066) 555-9701 |
-- | (338) 555-6650 | (704) 555-2131 |



-- Narrow pool of suspects by looking at the owners of cars left, money withdrawers and phon callers
SELECT *
FROM people
WHERE id IN
    (SELECT person_id
    FROM bank_accounts
    WHERE account_number IN (SELECT account_number FROM atm_transactions WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw'))
AND phone_number IN
    (SELECT caller FROM phone_calls WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60)
AND license_plate IN
    (SELECT license_plate FROM bakery_security_logs WHERE year = 2021 AND month = 7 AND day = 28 AND hour = 10 AND minute > 15 AND minute < 25 AND activity = 'exit');
-- |   id   | name  |  phone_number  | passport_number | license_plate |
-- +--------+-------+----------------+-----------------+---------------+
-- | 514354 | Diana | (770) 555-1861 | 3592750733      | 322W7JE       |
-- | 686048 | Bruce | (367) 555-5533 | 5773159633      | 94KL13X       |

-- Figuring out our 2 supect pairs
SELECT caller, receiver FROM phone_calls WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60 AND (caller = '(770) 555-1861' OR caller = '(367) 555-5533');
-- |     caller     |    receiver    |
-- +----------------+----------------+
-- | (367) 555-5533 | (375) 555-8161 |
-- | (770) 555-1861 | (725) 555-3243 |
SELECT * FROM people WHERE phone_number = '(375) 555-8161';
-- |   id   | name  |  phone_number  | passport_number | license_plate |
-- +--------+-------+----------------+-----------------+---------------+
-- | 864400 | Robin | (375) 555-8161 |                 | 4V16VO0       |
SELECT * FROM people WHERE phone_number = '(725) 555-3243';
-- |   id   |  name  |  phone_number  | passport_number | license_plate |
-- +--------+--------+----------------+-----------------+---------------+
-- | 847116 | Philip | (725) 555-3243 | 3391710505      | GW362R6       |

-- So either Diana and Philip // Bruce and Robin



-- Earliest flight out of Fiftyville the next day
SELECT *
FROM flights
WHERE year = 2021 AND month = 7 AND day = 29 AND
    (origin_airport_id = (SELECT id FROM airports WHERE city = 'Fiftyville'))
ORDER BY hour, minute
LIMIT 1;
-- | id | origin_airport_id | destination_airport_id | year | month | day | hour | minute |
-- +----+-------------------+------------------------+------+-------+-----+------+--------+
-- | 36 | 8                 | 4                      | 2021 | 7     | 29  | 8    | 20     |



-- Determine destination airport
SELECT *
FROM airports
WHERE id = 4;
-- | id | abbreviation |     full_name     |     city      |
-- +----+--------------+-------------------+---------------+
-- | 4  | LGA          | LaGuardia Airport | New York City |

-- Suspect ESCAPED TO New York City



-- Thief was on flight 36, which means passport number of thief is in
SELECT passport_number
FROM passengers
WHERE flight_id = 36;

-- | passport_number |
-- +-----------------+
-- | 7214083635      |
-- | 1695452385      |
-- | 5773159633      |
-- | 1540955065      |
-- | 8294398571      |
-- | 1988161715      |
-- | 9878712108      |
-- | 8496433585      |

SELECT name
FROM people
WHERE id IN
    (SELECT person_id
    FROM bank_accounts
    WHERE account_number IN (SELECT account_number FROM atm_transactions WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw'))
AND phone_number IN
    (SELECT caller FROM phone_calls WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60)
AND license_plate IN
    (SELECT license_plate FROM bakery_security_logs WHERE year = 2021 AND month = 7 AND day = 28 AND hour = 10 AND minute > 15 AND minute < 25 AND activity = 'exit')
AND passport_number IN
    (SELECT passport_number FROM passengers WHERE flight_id = 36);

-- Bruce is the THIEF

-- Which makes Robin the ACCOMPLICE
