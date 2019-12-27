#!/usr/bin/env python3

"""Convert the data into an array rows[month] and columns[year]"""

import os
import sys
import syslog

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-3]
NODE        = os.uname()[1]


def get_cli_params(expected_amount):
    """Check for presence of a CLI parameter."""
    if len(sys.argv) != (expected_amount + 1):
        print(f"{expected_amount} arguments expected, {len(sys.argv) - 1} received.")
        sys.exit(0)
    # 1 parameter required = filename to be processed
    return sys.argv[1]


def read_file(file_to_read_from):
    """
    Return the contents of a file if it exists.

    Abort if it doesn't exist.
    """
    if not os.path.isfile(file_to_read_from):
        sys.exit(0)
    with open(file_to_read_from, 'r') as input_file:
        # read the inputfile
        return input_file.read().splitlines()


def write_file(file_to_write_to, lines_to_write):
    """
    Output <lines_to_write> to the file <file_to_write_to>.

    Will overwrite existing file.
    """
    with open(file_to_write_to, 'w') as output_file:
        for line in lines_to_write:
            write_line = "; ".join(map(str,line))
            output_file.write(f'{write_line}\n')


def build_arrays(lines_to_process):
    """Use the input to build two arrays and return them.

     example input line : "2015-01; 329811; 0"  : YYYY-MM; T1; T2
     the list comes ordered by the first field
     the first line and last line can be inspected to find
     the first and last year in the dataset.
    """
    first_year = int(lines_to_process[0].split('; ')[0].split('-')[0])
    last_year = int(lines_to_process[-1].split('; ')[0].split('-')[0]) + 1
    num_years = last_year - first_year

    usage = [['maand'] + list(range(first_year, last_year))]
    production = [['maand'] + list(range(first_year, last_year))]
    for month in range(1,13):
        usage.append([month] + list([0] * num_years))
        production.append([month] + list([0] * num_years))

    for line in lines_to_process:
        data = line.split('; ')

        [year, month] = data[0].split('-')
        row_idx = int(month)
        col_idx = int(year) - first_year + 1
        usage[row_idx][col_idx] = int(data[1])
        production[row_idx][col_idx] = int(data[2])
    return production, usage


def build_arrays44(lbls, use_data, expo_data):
    """Use the input to build two arrays and return them.

     example input line : "2015-01; 329811; 0"  : YYYY-MM; T1; T2
     the list comes ordered by the first field
     the first line and last line can be inspected to find
     the first and last year in the dataset.
    """
    first_year = int(lbls[0].split('-')[0])
    last_year = int(lbls[-1].split('-')[0]) + 1
    num_years = last_year - first_year
    usage = list()
    export = list()

    label_lists = [list(range(first_year, last_year)), list(range(1,13))]
    for month in range(1,13):
        usage.append(list([0] * num_years))
        export.append(list([0] * num_years))

    for data_point in zip(lbls, use_data, expo_data):
        [year, month] = data_point[0].split('-')
        row_idx = int(month)
        col_idx = int(year) - first_year + 1
        usage[row_idx][col_idx] = data_point[1]
        export[row_idx][col_idx] = data_point[2]
    return label_lists, usage, export


if __name__ == "__main__":
    # initialise logging
    syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)
    IFILE = get_cli_params(1)
    FILE_LINES = read_file(IFILE)
    PRODUCTION_ARRAY, USAGE_ARRAY = build_arrays(FILE_LINES)

    write_file("".join([IFILE, "u"]), USAGE_ARRAY)
    write_file("".join([IFILE, "p"]), PRODUCTION_ARRAY)
