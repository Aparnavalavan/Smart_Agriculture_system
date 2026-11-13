
CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crop Recommendation History
CREATE TABLE IF NOT EXISTS crop_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    nitrogen REAL,
    phosphorus REAL,
    potassium REAL,
    temperature REAL,
    humidity REAL,
    ph REAL,
    rainfall REAL,
    recommended_crop TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

-- Plant Disease Screening History
CREATE TABLE IF NOT EXISTS disease_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    plant TEXT,
    symptom TEXT,
    result TEXT,
    advice TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

CREATE TABLE IF NOT EXISTS weather_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    city TEXT NOT NULL,
    temperature REAL,
    humidity REAL,
    wind REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);
