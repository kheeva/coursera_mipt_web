CREATE TABLE IF NOT EXISTS users_data
(
    telegram_id SERIAL,
    photo BYTEA,
    place_point point
);
