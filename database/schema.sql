IF EXISTS DROP DATABASE wishbone;
CREATE DATABASE wishbone;

CREATE TABLE game (
    game_id INT GENERATED ALWAYS AS identity (MINVALUE 1 START WITH 1 INCREMENT BY 1),
    game_name TEXT NOT NULL,
    retail_price INT NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE tracking (
    tracking_id INT GENERATED ALWAYS AS identity (MINVALUE 1 START WITH 1 INCREMENT BY 1),
    email TEXT NOT NULL,
    game_id INT NOT NULL,
    PRIMARY KEY(tracking_id),
    FOREIGN KEY (game_id) REFERENCES game(game_id)
);

CREATE TABLE platform(
    platform_id INT GENERATED ALWAYS AS identity (MINVALUE 1 START WITH 1 INCREMENT BY 1),
    platform_name TEXT NOT NULL,
    PRIMARY KEY(platform_id)
);

CREATE TABLE listing(
    listing_id INT GENERATED ALWAYS AS identity (MINVALUE 1 START WITH 1 INCREMENT BY 1),
    game_id INT NOT NULL,
    platform_id INT NOT NULL,
    price INT NOT NULL,
    discount_percent INT NOT NULL,
    recording_date DATE CHECK (recording_date <= CURRENT_DATE),
    PRIMARY KEY(listing_id),
    UNIQUE (game_id, platform_id, discount_percent, price, recording_date),
    FOREIGN KEY (game_id) REFERENCES game(game_id),
    FOREIGN KEY (platform_id) REFERENCES platform(platform_id)
);

