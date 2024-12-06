CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR,
    phone_number VARCHAR UNIQUE,
    mail VARCHAR UNIQUE,
    address VARCHAR,
    birth TIMESTAMP,
    sex VARCHAR,
    tabel_number INTEGER UNIQUE,
    segment VARCHAR,
    function VARCHAR
);

CREATE TABLE pets (
    pet_id SERIAL PRIMARY KEY,
    name VARCHAR,
    sex VARCHAR,
    owner_id INTEGER REFERENCES users(user_id),
    animal VARCHAR,
    breed VARCHAR,
    birth TIMESTAMP,
    weight INTEGER,
    sterilized BOOLEAN
);

CREATE TABLE passwords (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    login VARCHAR UNIQUE,
    password_hash VARCHAR UNIQUE
);

CREATE TABLE pets_feeds (
    pet_id INTEGER REFERENCES pets(pet_id),
    feed_name VARCHAR,
    feed_type VARCHAR,
    PRIMARY KEY (pet_id)
);

CREATE TABLE promos (
    promo_id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(user_id),
    activated_on TIMESTAMP,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    type VARCHAR,
    promo VARCHAR UNIQUE
);

CREATE TABLE statuses (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    status_type VARCHAR
);

CREATE TABLE pets_diseases (
    incident_id SERIAL PRIMARY KEY,
    pet_id INTEGER REFERENCES pets(pet_id),
    disease_name VARCHAR,
    disease_danger INTEGER
);