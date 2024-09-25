import sys
import socket

def remove_newline_from_str(s):
    return s.replace('\n', '')

# argv[0] is python file name, argv[1] is flow log file path
if len(sys.argv) != 2:
    print("Script expected path to flow log file. Quitting.")
    sys.exit()


# Read and store data from flow log input file into list
flow_log_file_name = sys.argv[1]
flow_log_lines = []
with open(flow_log_file_name) as file:
    flow_log_lines = file.readlines()


# Read and store lookup table into a dict with the following key:value format:
#      << TUPLE >>      : << STRING >>
#  (dstport, protocol)  :     tag
#
# Also, create dict for protocol value (int) : protocol name (str) for translating protocol int to str
#      << INT >>  : << STRING >>
#          6      :     'tcp'
lookup_table_file_name = "input_files/lookup_table.csv"
lookup = {}
to_protocol_str = {}
lookup_table_lines = []
with open(lookup_table_file_name) as file:
    lookup_table_lines = file.readlines()

# Parse lookup csv file; skip first line of column headers.
# Each line is in the following format:
#   Column: dstport | protocol | tag
#   Index:     0    |    1     |  2
# Ex. lookup stored in dict: ('25', 'tcp') : 'sv_P1'
for i in range(1, len(lookup_table_lines)):
    lookup_split = lookup_table_lines[i].replace('\n', '').split(',')
    dstport = lookup_split[0]
    protocol_str = lookup_split[1]
    tag = lookup_split[2]

    # Add new lookup to local dict
    key_tuple = (dstport, protocol_str)
    lookup[key_tuple] = tag

    # Add protocol value : protocol name to translation dict
    protocol_val = socket.getprotobyname(protocol_str)
    to_protocol_str[protocol_val] = protocol_str


# Each flow log line is in the following format: (see AWS docs link in README for more info)
#   Column: version | account-id | interface-id | srcaddr | dstaddr | srcport | dstport | protocol | packets | bytes | start | end | action | log-status
#   Index:     0    |      1     |      2       |    3    |    4    |    5    |    6    |    7     |    8    |   9   |  10   | 11  |   12   |    13
for flow_log_line in flow_log_lines:
    flow_log_split = flow_log_line.replace('\n', '').split(' ')

    dstport = flow_log_split[6]
    protocol = flow_log_split[7]

