CREATE TABLE IF NOT EXISTS users_data
(
    telegram_id SERIAL,
    name VARCHAR(128),
    photo BYTEA,
    place_point point,
    timestamp timestamp default current_timestamp
);
