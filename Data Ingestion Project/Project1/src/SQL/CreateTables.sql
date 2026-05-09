-- The correct way to drop all tables respecting referential integrity
DROP TABLE IF EXISTS Social_Behavior;
DROP TABLE IF EXISTS Technology_Usage;
DROP TABLE IF EXISTS Shopping_Behavior;
DROP TABLE IF EXISTS Shopping_Preference;
DROP TABLE IF EXISTS Invalid_Entries;
DROP TABLE IF EXISTS Customers;

-- creating Customers table
-- PK: customer_id
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    age INT NOT NULL,
    monthly_income DECIMAL(10,2) NOT NULL
);

-- creating Technology_Usage table
-- PK: technology_usage_id
-- FK: customer_id from Customers table
CREATE TABLE Technology_Usage (
    technology_usage_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    daily_internet_hours DECIMAL(10,2) NOT NULL,
    smartphone_usage_years DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- creating Social_Behavior table
-- PK: social_behavior_id
-- FK: customer_id from Customers table
CREATE TABLE Social_Behavior (
    social_behavior_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    social_media_hours DECIMAL(10,2) NOT NULL,
    online_payment_trust_score DECIMAL(10,2) NOT NULL,
    tech_savvy_score DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- creating Shopping_Preference table
-- PK: shopping_preference_id
CREATE TABLE Shopping_Preference (
    shopping_preference_id INT PRIMARY KEY,
    preference_name VARCHAR(50) NOT NULL
);

-- creating Shopping_Behavior table
-- PK: shopping_behavior_id
-- FK: customer_id from Customers table
-- FK: shopping_preference_id from Shopping_Preference table
CREATE TABLE Shopping_Behavior (
    shopping_behavior_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    monthly_online_orders INT NOT NULL,
    monthly_store_visits INT NOT NULL,
    avg_online_spend DECIMAL(10,2) NOT NULL,
    shopping_preference_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (shopping_preference_id) REFERENCES Shopping_Preference(shopping_preference_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- creating Invalid_Entries table
-- PK: invalid_entry_id
CREATE TABLE Invalid_Entries ( -- entries containing null values or were duplicates
    invalid_entry_id SERIAL PRIMARY KEY,
    age INT,
    monthly_income DECIMAL(10,2),
    daily_internet_hours DECIMAL(10,2),
    smartphone_usage_years DECIMAL(10,2),
    social_media_hours DECIMAL(10,2),
    online_payment_trust_score DECIMAL(10,2),
    tech_savvy_score DECIMAL(10,2),
    monthly_online_orders INT,
    monthly_store_visits INT,
    avg_online_spend DECIMAL(10,2),
    shopping_preference VARCHAR(50)
);