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
             'sql_command': "INSERT INTO production ("
                            "sample_time, sample_epoch, site_id, energy"
                            ") "
                            "VALUES (?, ?, ?, ?)",
             'reporttime': 899,
             'cycles': 1,
             'samplespercycle': 1
             }

ZAPPI = {'database': _DATABASE,
         'sql_commmand': "INSERT INTO zappi ("
                         "sample_time, sample_epoch"
                         ") "
                         "VALUES (?, ?, ?, ?)",
         'director': "https://director.myenergi.net",
         'template': {'hr': 0,
                      'dow': "Mon",
                      'dom': 1,
                      'mon': 1,
                      'yr': 2021,
                      'exp': 0.0,
                      'gen': 0.0,
                      'gep': 0.0,
                      'imp': 0.0,
                      'h1b': 0.0,
                      'h1d': 0.0,
                      }
         }
