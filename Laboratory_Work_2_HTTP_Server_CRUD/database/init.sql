-- Create Table Price
CREATE TABLE price (
    id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2),
    currency VARCHAR(3)
);

-- Create Table Phone
CREATE TABLE phone (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title VARCHAR(255) NOT NULL,
    price_currency_id INT REFERENCES price(id),
    description TEXT
);