#!/usr/bin/env python3

import os

_MYHOME = os.environ["HOME"]
_DATABASE = "/mnt/data/electriciteit.sqlite3"
if not os.path.isfile(_DATABASE):
    _DATABASE = f"{_MYHOME}/.sqlite3/electriciteit.sqlite3"

BATTERY = {'database': _DATABASE,
           'graph_file': ".local/graph.png"
           }

KAMSTRUP = {'database': _DATABASE,
            'sql_command': "INSERT INTO kamstrup ("
                           "sample_time, sample_epoch, "
                           "T1in, T2in, powerin, "
                           "T1out, T2out, powerout, "
                           "tarif, swits"
                           ") "
                           "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            'report_time': 600,
            'cycles': 1,
            'samplespercycle': 58
            }

SOLAREDGE = {'database': _DATABASE,
             'reporttime': 899,
             'cycles': 1,
             'samplespercycle': 1,
             'sql_commmand': "INSERT INTO production ("
                             "sample_time, sample_epoch, site_id, energy"
                             ") "
                             "VALUES (?, ?, ?, ?)"
             }

ZAPPI = {'database': _DATABASE,
         'sql_commmand': "INSERT INTO zappi ("
                         "sample_time, sample_epoch"
                         ") "
                         "VALUES (?, ?, ?, ?)"
         }
