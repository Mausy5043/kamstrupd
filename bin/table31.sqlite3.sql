# SQLite3 script
# create table for KAMSTRUP smart electricity meter readings
# create table for SOLAREDGE solar panel monitoring
# create table for power production registration

DROP TABLE IF EXISTS kamstrup;

CREATE TABLE kamstrup (
  sample_time   datetime NOT NULL PRIMARY KEY,
  sample_epoch  integer,
  T1in          integer,
  T2in          integer,
  powerin       integer,
  T1out         integer,
  T2out         integer,
  powerout      integer,
  tarif         integer,
  swits         integer
  );

# SQLite3 automatically creates a UNIQUE INDEX on the PRIMARY KEY in the background.
# So, no index needed.


# T1* and T2* are stored in [Wh]
# power* is stored in [W]
# tarif and swits are either a `1` or a `2`

-- DROP TABLE IF EXISTS solaredge;

-- CREATE TABLE solaredge (
--   id            integer PRIMARY KEY AUTOINCREMENT,
--   sample_time   datetime,
--   sample_epoch  integer,
--   panel_id      integer,
--   vac           integer,
--   vdc           integer,
--   power         integer,
--   frequency     integer,
--   temperature   integer
--   );

-- CREATE INDEX idx_panel ON solaredge(panel_id);
-- CREATE INDEX idx_time ON solaredge(sample_time);

DROP TABLE IF EXISTS production;

CREATE TABLE production (
  id            integer PRIMARY KEY AUTOINCREMENT,
  sample_time   datetime,
  sample_epoch  integer,
  site_id       integer,
  energy        integer
  );

CREATE INDEX idx_site ON production(site_id);
CREATE INDEX idx_date ON production(sample_time);

# Set a starting value and add first two datapoints (not available in SolarEdge DB)
INSERT INTO production (sample_time, sample_epoch, site_id, energy) VALUES ('2020-02-20 09:08:22', 1582186102, 1508443, 0);
INSERT INTO production (sample_time, sample_epoch, site_id, energy) VALUES ('2020-02-21 23:30:00', 1582324200 , 1508443, 510);
INSERT INTO production (sample_time, sample_epoch, site_id, energy) VALUES ('2020-02-22 09:30:00', 1582360200 , 1508443, 641);


DROP TABLE IF EXISTS zappi;

CREATE TABLE zappi (
    id            integer PRIMARY KEY AUTOINCREMENT,
    sample_time   datetime,
    sample_epoch  integer,
    site_id       integer
    -- other fields to be added
    );

# SQLite3 automatically creates a UNIQUE INDEX on the PRIMARY KEY in the background.
# So, no index needed.
