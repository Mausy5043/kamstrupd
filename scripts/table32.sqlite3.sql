# SQLite3 script
# create table for weather station data

DROP TABLE IF EXISTS weather;

CREATE TABLE weather (
  sample_time   datetime NOT NULL PRIMARY KEY,
  sample_epoch  integer,
  temperature   float,
  solrad        float
  );

# SQLite3 automatically creates a UNIQUE INDEX on the PRIMARY KEY in the background.
# So, no index needed.

CREATE INDEX idx_epoch ON weather(sample_epoch);
