"""Tool that normalizes SCPI commands/responses to use full path, one per line.
"""

import sys
import argparse


def _parse_command_line():
    """Parses the command line for the main function.
    """
    desc_message =  "Tool that normalizes SCPI commands/responses to use full path, one per line."
    parser = argparse.ArgumentParser(
                    prog='scpi_normalize',
                    description=desc_message)

    parser.add_argument('-i', '--in-file',
                        help="Input file name that contains raw SCPI commands or responses.  "
                             "Default is to use stdin.",
                        default=None,
                        action='store')
    parser.add_argument('-o', '--out-file',
                        help="Normalized output file name.  Default is to use stdout.",
                        default=None,
                        action='store')
    parser.add_argument('-S', '--no-sort',
                        help="Disables sorting of the lines.  Default is to sort.",
                        default=False,
                        action='store_true')

    args = parser.parse_args()

    return args


def _main():
    """The main function when this module is executed as a command-line program.
    """
    # pylint: disable=consider-using-with

    args = _parse_command_line()

    input_file  = sys.stdin
    output_file = sys.stdout

    if args.in_file is not None:
        input_file = open( args.in_file, 'rt', encoding='ascii', newline=None )
    if args.out_file is not None:
        output_file = open( args.out_file, 'wt+', encoding='ascii' )


    # Walk the lines in the file, use ';' as a command separator, then split
    # the key from value using 1st space.
    current_path = ':'
    output = []
    for line in input_file:
        commands = line.split(';')
        for command in commands:
            command = command.lstrip().rstrip()
            key_value = command.partition(' ')
            key = key_value[0]
            key.upper()
            # Skip blank lines
            if len(key) == 0:
                continue
            if key[0] != ':':
                key = current_path + key
            # Guaranteed to be at least 1 ':'.  Extract path for the key and update current_path
            colon_last  = key.rfind(':')
            current_path = key[:colon_last+1]
            output.append( f"{key}{key_value[1]}{key_value[2]}\n" )

    if not args.no_sort:
        output.sort()

    for line in output:
        output_file.write( line )

    if output_file is not sys.stdout:
        output_file.close()
    if input_file is not sys.stdin:
        input_file.close()

if __name__ == "__main__":
    _main()
