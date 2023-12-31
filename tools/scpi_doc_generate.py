"""Tool that normalizes SCPI commands/responses to use full path, one per line.
"""

import sys
import argparse


def _parse_command_line():
    """Parses the command line for the main function.
    """
    desc_message =  "Tool that generates documentation for SCPI.  Both input files for verbose " \
                    "and terse format must be specified, though both can refer to the same " \
                    "file.  Both files should have the same number of lines and the lines are " \
                    "in the same order with the only difference between verbose vs terse " \
                    "format.  Both files must be normalized."
    parser = argparse.ArgumentParser(
                    prog='scpi_normalize',
                    description=desc_message)

    parser.add_argument('-v', '--in-file-verbose',
                        help="Input file name that contains normalized SCPI commands or responses "
                             "originally generated using ':VERBOSE ON' mode (i.e. long paths).",
                        default=None,
                        action='store')
    parser.add_argument('-t', '--in-file-terse',
                        help="Input file name that contains normalized SCPI commands or responses "
                             "originally generated using ':VERBOSE OFF' mode (i.e. short paths).",
                        default=None,
                        action='store')
    parser.add_argument('-o', '--out-file',
                        help="Normalized output file name.  Default is to use stdout.",
                        default=None,
                        action='store')
    parser.add_argument('-f', '--format-file',
                        help="Format file name whose contents are used for each line from the " \
                             "input file to generate what goes into the output file.  Use " \
                             "'$PATH$' in the format file for where the path text will go.  " \
                             "Similarly, use '$VALUE$' for the example value text.",
                        default=None,
                        action='store')

    args = parser.parse_args()

    return args


def _parse_input_file( input_file ):
    paths_and_values = []
    for line in input_file:
        key_value = line.partition(' ')
        path_segments = key_value[0].upper().split(':')
        if len( path_segments ) > 1 and len( path_segments[0] ) == 0 :
            path_segments.pop(0)
        new_key_value = []
        new_key_value.append( path_segments )
        new_key_value.append( key_value[1] )
        new_key_value.append( key_value[2] )
        paths_and_values.append( new_key_value )
    return paths_and_values


def _main():
    """The main function when this module is executed as a command-line program.
    """
    # pylint: disable=consider-using-with,consider-using-enumerate,too-many-locals,invalid-name

    EOL = '\n'

    args = _parse_command_line()
    if args.in_file_verbose is None or args.in_file_terse is None:
        print( "Error: both --in-file-verbose and --in-file-terse are required." )
        sys.exit(1)
    if args.format_file is None:
        print( "Error: --format-file is required." )
        sys.exit(1)

    output_file = sys.stdout

    input_file_verbose = open( args.in_file_verbose, 'rt', encoding='ascii', newline=None )
    input_file_terse   = open( args.in_file_terse,   'rt', encoding='ascii', newline=None )
    if args.out_file is not None:
        output_file = open( args.out_file, 'wt+', encoding='ascii' )
    format_string = ""
    with open( args.format_file, 'rt', encoding='ascii', newline=None) as file:
        format_string = file.read()

    paths_and_values_verbose = _parse_input_file( input_file_verbose )
    paths_and_values_terse   = _parse_input_file( input_file_terse )

    if len(paths_and_values_verbose) != len( paths_and_values_terse ):
        print( "ERROR: the two input files have different number of lines." )
        sys.exit(1)

    paths_and_values = []
    for i in range(0, len(paths_and_values_verbose) ):
        path_seg_verbose = paths_and_values_verbose[i][0]
        paths_terse   = paths_and_values_terse[i][0]
        if len( path_seg_verbose ) != len( paths_terse ):
            print( f"ERROR: line {i} shows has lines from each file with different number of " \
                    "path segments." )
            sys.exit(1)

        path = ""
        for j in range( 0, len( path_seg_verbose ) ):
            if not path_seg_verbose[j].startswith( paths_terse[j] ):
                print( f"ERROR: line {i} path segment {path_seg_verbose[j]} does not start " \
                       f"with {paths_terse[j]}." )
                sys.exit(1)
            path_seg = paths_terse[j] + path_seg_verbose[j][ len(paths_terse[j]): ].lower()
            path = path + ':' + path_seg
        paths_and_values.append( [ path, paths_and_values_verbose[i][2] ] )

    for path_and_value in paths_and_values:
        line = format_string
        line = format_string.replace( '$PATH$', path_and_value[0] )
        line = line.replace( '$VALUE$', path_and_value[1].rstrip(EOL) )
        # The format could be loaded from a file in the future to be more flexible.
        output_file.write( line )

    if output_file is not sys.stdout:
        output_file.close()
    input_file_terse.close()
    input_file_verbose.close()

if __name__ == "__main__":
    _main()
