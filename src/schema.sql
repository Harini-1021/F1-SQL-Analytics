CREATE TABLE drivers (
    driver_id     INTEGER PRIMARY KEY,
    driver_ref    TEXT NOT NULL,
    number        INTEGER,
    code          TEXT,
    forename      TEXT NOT NULL,
    surname       TEXT NOT NULL,
    dob           DATE,
    nationality   TEXT
);

CREATE TABLE constructors (
    constructor_id   INTEGER PRIMARY KEY,
    constructor_ref  TEXT NOT NULL,
    name             TEXT NOT NULL,
    nationality      TEXT
);

CREATE TABLE circuits (
    circuit_id    INTEGER PRIMARY KEY,
    circuit_ref   TEXT NOT NULL,
    name          TEXT NOT NULL,
    location      TEXT,
    country       TEXT,
    lat           REAL,
    lng           REAL,
    alt           INTEGER
);

CREATE TABLE status (
    status_id   INTEGER PRIMARY KEY,
    status      TEXT NOT NULL
);

CREATE TABLE races (
    race_id      INTEGER PRIMARY KEY,
    year         INTEGER NOT NULL,
    round        INTEGER NOT NULL,
    circuit_id   INTEGER NOT NULL,
    name         TEXT NOT NULL,
    date         DATE,
    FOREIGN KEY (circuit_id) REFERENCES circuits(circuit_id)
);

CREATE TABLE results (
    result_id          INTEGER PRIMARY KEY,
    race_id            INTEGER NOT NULL,
    driver_id          INTEGER NOT NULL,
    constructor_id     INTEGER NOT NULL,
    grid               INTEGER,
    position           INTEGER,
    position_order     INTEGER NOT NULL,
    points             REAL NOT NULL DEFAULT 0,
    laps               INTEGER,
    milliseconds       INTEGER,
    fastest_lap_time   TEXT,
    fastest_lap_speed  REAL,
    status_id          INTEGER NOT NULL,
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (constructor_id) REFERENCES constructors(constructor_id),
    FOREIGN KEY (status_id) REFERENCES status(status_id)
);