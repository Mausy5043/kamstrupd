# SQLite3 script
# create table for KAMSTRUP smart electricity meter reaadings
# create tabel for SOLAREDGE solar panel monitoring

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

DROP TABLE IF EXISTS solaredge;

CREATE TABLE solaredge (
  id            integer PRIMARY KEY AUTOINCREMENT,
  sample_time   datetime,
  sample_epoch  integer,
  panel_id      integer,
  vac           integer,
  vdc           integer,
  power         integer,
  frequency     integer,
  temperature   integer
  );

CREATE INDEX idx_panel ON solaredge(panel_id);
CREATE INDEX idx_time ON solaredge(sample_time);
