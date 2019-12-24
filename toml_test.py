import toml
import sys
import argparse
import os
from datetime import datetime

# Get the public IP address of the server using the OpenDNS.
command_stream = os.popen('dig +short myip.opendns.com @resolver1.opendns.com')
public_ip = command_stream.read().strip()

parser = argparse.ArgumentParser(description="Set or reset IP addresses in all WebRTC agents' TOML files.")

# If OpenDNS couldn't be reached or the server IP couldn't be fetched, ask the user to supply the IP address
if(public_ip is None or len(public_ip) == 0):
    parser.add_argument('--ip', dest='ip', help='The public IP address of this WebRTC server', required=True, metavar='xxx.xxx.xxx.xxx')

# Get the OWT server's installation directory.
parser.add_argument('--dir', dest='owt_server_dir', help="Path to the directory containing the OWT server's agents", required=False)

# Parse the command line arguments and get the values
args = parser.parse_args()

if(hasattr(args, 'ip')):
    public_ip = args.ip

server_dir = args.owt_server_dir or '.'

# Get all the agent folders in the OWT server's directory
for name in os.listdir(server_dir):
    # Iterate over each folder and parse the TOML file and set the IP address.
    dir_path = os.path.join(server_dir, name)
    if os.path.isdir(dir_path) and '_agent' in name:

        toml_filename = "agent.toml"
        toml_filepath = os.path.join(dir_path, toml_filename)
        toml_file = open(toml_filename, "r") #TODO: Change this to toml_filepath
        toml_text = toml_file.read()

        # Save a backup of the file in agent.toml.old.timestamp
        backup_filename = toml_filename.split('.')[0] + '.' + datetime.now().isoformat().replace(':', '.') + '.' + toml_filename.split('.')[1]
        backup_file = open(backup_filename, "w")
        backup_file.write(toml_text)
        backup_file.close()

        parsed_toml = toml.loads(toml_text)

        internal_key = "internal"
        ip_key = "ip_address"

        if(internal_key in parsed_toml.keys() and ip_key in parsed_toml[internal_key].keys()):
            parsed_toml['internal']['ip_address'] = public_ip

        toml_string = toml.dumps(parsed_toml)

        # Save the TOML file.
