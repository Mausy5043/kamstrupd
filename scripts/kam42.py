#!/usr/bin/env python3

"""Calculate statistics per hour"""

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

     example input line : "022 10; 418; 0"  : JJJ-HH; T1; T2
     the list comes ordered by the first field
     the first line and last line can be inspected to find
     the first and last year in the dataset.
    """

    usage = [[] for x in range(0,24)]
    production = [[] for x in range(0,24)]

    for line in lines_to_process:
        data = line.split('; ')

        [day, hour] = data[0].split('-')
        row_idx = int(hour)
        usage[row_idx].append(int(data[1]))
        production[row_idx].append(int(data[2]))
    return production, usage


if __name__ == "__main__":
    # initialise logging
    syslog.openlog(ident=MYAPP, facility=syslog.LOG_LOCAL0)
    IFILE = get_cli_params(1)
    FILE_LINES = read_file(IFILE)
    PRODUCTION_ARRAY, USAGE_ARRAY = build_arrays(FILE_LINES)

    write_file("".join([IFILE, "u"]), USAGE_ARRAY)
    write_file("".join([IFILE, "p"]), PRODUCTION_ARRAY)
