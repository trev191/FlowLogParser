This parser program will take in a [flow log data](https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html) file and map each row to a tag based on a lookup table.

Those mappings are then processed to produce an output csv file containing:
- Count of matches for each tag
- Count of matches for each port/protocol combination

## How to use the program:
#### NOTE: Python and git must be installed on the system
1. Open a command prompt/terminal
2. Clone git repo
   - <code>git clone https://github.com/trev191/FlowLogParser.git</code>
3. Navigate into the newly cloned folder
   - <code>cd FlowLogParser</code>
5. Run the script with the flow logs file as an argument
   - <code>python flow_log_parser.py \<input flow logs file\></code>
     - Ex. <code>python flow_log_parser.py input_files/sample_flow_logs.txt</code>

#### For further desired customization/testing, the following files may be updated/created:
  - <code>input_files/lookup_table.csv</code>
  - <code>input_files/\<new input flow logs file\></code>

## Program assumptions:
- The inputted flow log file is in the default log format (version 2)
- The inputted flow log file size can be up to 10 MB
- The lookup file can have up to 10000 mappings
- The tags can map to more than one port, protocol combinations
- Matches are case insensitive (and therefore all tags are converted to lowercase)
