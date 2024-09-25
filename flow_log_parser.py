import sys
import socket

# Validate we received a single argument (the flow log file path)
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
#
# Parse each flow log line and use data to count up tag matches and port/protocol matches
# to be later recorded to output file
tag_matches = {}
port_protocol_matches = {}
for flow_log_line in flow_log_lines:
    flow_log_split = flow_log_line.replace('\n', '').split(' ')

    # Parse necessary data from flow log and create tuple to be used as key for lookup table
    dstport = flow_log_split[6]
    protocol_val = flow_log_split[7]
    protocol_str = to_protocol_str[int(protocol_val)]
    key_tuple = (dstport, protocol_str)

    # Add up matches for each tag. Increment by 1 if key:value
    # already exists, otherwise initialize it to 1 
    #
    # If we found matching tag, add to tag name count in dict
    if lookup.get(key_tuple) != None:
        # TODO: add a method for case insensitive tags
        tag = lookup[key_tuple]
        tag_matches[tag] = tag_matches.get(tag, 0) + 1
    # Else no matching tag, add to "Untagged" count in dict
    else:
        tag_matches["Untagged"] = tag_matches.get("Untagged", 0) + 1

    # Add up matches for each dstport/protocol combination.
    # Increment by 1 if key:value already exists, otherwise
    # initialize it to 1
    port_protocol_matches[key_tuple] = port_protocol_matches.get(key_tuple, 0) + 1


# Write tag matches and port protocol matches to an output csv file