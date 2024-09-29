import subprocess
import sys

# environment variables
duration = 0
req_per_sec = 50

ansible_hostname = sys.argv[1]
command_type = sys.argv[2]
algo = sys.argv[3]
scheduler = sys.argv[4]
energy_ansible_path = f'/home/{ansible_hostname}/kubernetes-energy/ansible/'
inventory_file = f'{energy_ansible_path}inventory.yaml' 

def setup_workload():
    # setup benchmark log files
    setup_command = ["ansible-playbook", "-i", f"{energy_ansible_path}inventory.yaml", "-t", "setup_scaph", "e", f"scheduler={scheduler} algo={algo} req_per_sec={req_per_sec} dur={duration}", f"{energy_ansible_path}playbook-scaph.yaml"]
    rs = subprocess.run(setup_command, capture_output=True)
    print(rs.stdout)
    print(f"benchmark log files have been setup for {algo}")
    
    # enable scaphandre service
    enable_command = ["ansible-playbook", "-i", f"{energy_ansible_path}inventory.yaml", "-t", "enable_scaph", f"{energy_ansible_path}playbook-scaph.yaml"]
    rs = subprocess.run(enable_command, capture_output=True)
    print(rs.stdout)
    print(f"scaphandre service for {algo} has been setup across all nodes")

def remove_workload():
    disable_command = ["ansible-playbook", "-i", f"{energy_ansible_path}inventory.yaml", "-t", "disable_scaph", f"{energy_ansible_path}playbook-scaph.yaml"]
    rs = subprocess.run(disable_command, capture_output=True)
    print(rs.stdout)
    print(f"scaphandre service for {algo} has been disabled across all nodes")

def main():
    if command_type == 'setup':
        setup_workload()
    else:
        remove_workload()


if __name__ == "__main__":
    main()
