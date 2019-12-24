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

timestamp = datetime.now().isoformat().replace(':', '.')

print(server_dir)
# Get all the agent folders in the OWT server's directory
for name in os.listdir(server_dir):
    # Iterate over each folder and parse the TOML file and set the IP address.
    dir_path = os.path.join(server_dir, name)
    print(dir_path)
    if os.path.isdir(dir_path) and '_agent' in name:
        current_folder = dir_path.split('/')[-1]
        print(current_folder)
        toml_filename = "agent.toml"
        toml_filepath = os.path.join(dir_path, toml_filename)
        toml_file = open(toml_filepath, "r")
        toml_text = toml_file.read()
        toml_file.close()

        # Save a backup of the file in agent.toml.old.timestamp
        backup_filename = toml_filename.split('.')[0] + '.' + timestamp + '.' + toml_filename.split('.')[1]
        backup_filepath = os.path.join(server_dir, current_folder, backup_filename)
        backup_file = open(backup_filepath, "w")
        backup_file.write(toml_text)
        backup_file.close()

        parsed_toml = toml.loads(toml_text)

        internal_key = "internal"
        ip_key = "ip_address"

        if(internal_key in parsed_toml.keys() and ip_key in parsed_toml[internal_key].keys()):
            parsed_toml[internal_key][ip_key] = public_ip

        webrtc_key = "webrtc"
        network_interfaces_key = "network_interfaces"
        net_interface_name_key = "name"
        replaced_ip_key = "replaced_ip_address"

        # If the current directory is 'webrtc_agent', update the 'network_interfaces' member
        if current_folder == "webrtc_agent" and webrtc_key in parsed_toml.keys() and network_interfaces_key in parsed_toml[webrtc_key].keys():
            if len(parsed_toml[webrtc_key][network_interfaces_key]) != 0:
                parsed_toml[webrtc_key][network_interfaces_key] = []

            network_interface = dict({net_interface_name_key: "eth0", replaced_ip_key: public_ip})
            parsed_toml[webrtc_key][network_interfaces_key].append(network_interface)

        # Save the TOML file.
        toml_text = toml.dumps(parsed_toml)
        toml_file = open(toml_filepath, "w")
        toml_file.write(toml_text)
        toml_file.close()
