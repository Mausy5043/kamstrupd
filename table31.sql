# MySQL script
# create table for KAMSTRUP smart electricity meter readings

USE domotica;

DROP TABLE IF EXISTS kamstrup;

CREATE TABLE `kamstrup` (
  `sample_time`   datetime,
  `sample_epoch`  bigint(20) unsigned,
  `T1in`          int(11),
  `T2in`          int(11),
  `powerin`       int(11),
  `T1out`         int(11),
  `T2out`         int(11),
  `powerout`      int(11),
  `tarif`         int(11),
  `swits`         int(11),
  PRIMARY KEY (`sample_time`),
  INDEX (`sample_epoch`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;

# T1* and T2* are stored in [Wh]
# power* is stored in [W]
# tarif and swits are either a `1` or a `2`
