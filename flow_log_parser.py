import sys
import socket
import time

# Validate we received a single argument (the flow log file path)
# argv[0] is python file name, argv[1] is flow log file path
if len(sys.argv) != 2:
    print("Script expected path to flow log file. Quitting.")
    sys.exit()


# Read and store data from flow log input file into list
flow_log_file_name = sys.argv[1]
flow_log_lines = []
try:
    with open(flow_log_file_name, 'r') as input_file:
      flow_log_lines = input_file.readlines()
except FileNotFoundError:
    print("Inputted flow log file " + flow_log_file_name + " could not be found. Quitting.")
    sys.exit()


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
try:
  with open(lookup_table_file_name, 'r') as input_file:
      lookup_table_lines = input_file.readlines()
except FileNotFoundError:
    print("Lookup table file could not be found at " + lookup_table_file_name + ". Quitting.")
    sys.exit()


# Parse lookup csv file; skip first line of column headers.
# Each line is in the following format:
#   Column: dstport | protocol | tag
#   Index:     0    |    1     |  2
# Since matches are case insensitive, tag strings are updated to lowercase
# Ex. lookup stored in dict: ('25', 'tcp') : 'sv_P1'
for i in range(1, len(lookup_table_lines)):
    lookup_split = lookup_table_lines[i].replace('\n', '').split(',')
    dstport = lookup_split[0]
    protocol_str = lookup_split[1]
    tag = lookup_split[2].lower()

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
        tag = lookup[key_tuple]
        tag_matches[tag] = tag_matches.get(tag, 0) + 1
    # Else no matching tag, add to "Untagged" count in dict
    else:
        tag_matches["Untagged"] = tag_matches.get("Untagged", 0) + 1

    # Add up matches for each dstport/protocol combination.
    # Increment by 1 if key:value already exists, otherwise
    # initialize it to 1
    port_protocol_matches[key_tuple] = port_protocol_matches.get(key_tuple, 0) + 1


# Write tag matches and port/protocol matches to output csv file with Unix timestamp (seconds)
output_file_name = "output_files/output_" + str(int(time.time())) + ".csv"
with open(output_file_name, 'w') as output_file:
    # Write tag matches
    tag_matches_title = "Tag Counts:\n"
    output_file.write(tag_matches_title)
    tag_matches_headers = "Tag,Count\n"
    output_file.write(tag_matches_headers)
    for tag, count in tag_matches.items():
        row = tag + ',' + str(count) + '\n'
        output_file.write(row)
    output_file.write('\n')

    # Write port/protocol matches
    port_protocol_matches_title = "Port/Protocol Combination Counts:\n"
    output_file.write(port_protocol_matches_title)
    port_protocol_matches_headers = "Port,Protocol,Count\n"
    output_file.write(port_protocol_matches_headers)
    for key_tuple, count in port_protocol_matches.items():
        port, protocol_str = key_tuple
        row = port + ',' + protocol_str + ',' + str(count) + '\n'
        output_file.write(row)

    print("Results have been recorded at " + output_file_name)