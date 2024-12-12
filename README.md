# Kubernetes-energy-consumption

This repository provides the code, data, and instructions required to produce the results presented in the paper, "Energy Consumption of Heuristic-based Kubernetes Schedulers"

## Quick Start
### Prerequisites
- continuum framework: This is used to setup the VM cluster. Link: [continuum](https://github.com/atlarge-research/continuum)
- scaphandre: This is used for energy consumption tracking in the cluster. Link: [scaphandre](https://github.com/hubblo-org/scaphandre)
- ansible: Used to setup and run workloads. Link: [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

### Modified Benchmark Repos
Certain changes had to be made to the original benchmark and scheduler repos, our modified benchmark and scheduler repos are given below:
- [DeathStarBench](https://github.com/AlfredDaimari/DeathStarBench.git)
- [Descheduler](https://github.com/AlfredDaimari/descheduler)
- [Poseidon](https://github.com/AlfredDaimari/poseidon)

## Installation

### Setup continuum cluster
**Step 1:** Install continuum framework, click [here](https://github.com/atlarge-research/continuum) for instructions on setting up and installing continnum framework

**Step 2:** Basic settings for a 3 server cluster (the ones used for our benchmarks)
```
cat > basic.cfg <<EOF
[infrastructure]
provider = qemu

cloud_nodes = 3
cloud_cores = 4
cloud_memory = 16
cloud_quota = 1.0

middleIP = 138
middleIP_base = 139
base_path = /mnt/sdc/store

[benchmark]
resource_manager = kubernetes
resource_manager_only = True
EOF
```
**Step 3:** Use continuum to setup vm cluster
```
# continnum cluster setup (in the continuum directory)
continuum.py basic.cfg
```
**Step 4:** Remember to store the ssh keys, machine name for each vm in the cluster in a file

### Setup scaphandre
**Step 1:** Install scaphandre on the host, click [here](https://hubblo-org.github.io/scaphandre-documentation/tutorials/compilation-linux.html) for linux compilation. **Remember to install qemu feature with cargo**

**Step 2:** Create scaphandre service on host using the qemu option, click [here](https://hubblo-org.github.io/scaphandre-documentation/how-to_guides/propagate-metrics-hypervisor-to-vm_qemu-kvm.html) for steps for setting up scaphandre on vms. If this does not work, follow the NFS guide below 

### Setup Scaphandre with NFS
**Step 1:** Run scaphandre on host/hypervisor machine (Ideally convert this into a service, such that it restarts on failure).
```
scaphandre qemu
```
**Step 2:** Expose scaphandre vm metrics using NFS
```
# add the following lines to your /etc/exports file 
/var/lib/libvirt/scaphandre/cloud0_user*(ro,sync,no_subtree_check,fsid=0)
/var/lib/libvirt/scaphandre/cloud1_user *(ro,sync,no_subtree_check,fsid=2)
/var/lib/libvirt/scaphandre/cloud_controller_user *(ro,sync,no_subtree_check,fsid=1)
```
After adding the above lines, restart the NFS Server. **Note: the user is your linux username, the libvirt scaphandre directory should have the name of the vms**

### Setup workload generator
A binary to run workload defined in lua files needs to be built. Follow the steps below to build the binary.
```
# change working directory to deathStarBench (our modified repo)
cd DeathStarBench

# run build command
```

### Install prequisites in cluster
For the benchmarks to run, prerequisites need to be installed in the cluster. 
```
# clone this repository
git clone https://github.com/AlfredDaimari/kubernetes-energy

# before running the commands below
# make changes to the ansible/inventory.yaml file with your cluster details
# continuum should log out your cluster detials, it can also be found on continuum logs

# install scaph on each vm
cd ansible
ansible-playbook -i inventory.yaml -t install_scaph playbook-scaph.yaml

# setup nfs server
ansible-playbook -i inventory.yaml -t nfs_setup playbook-scaph.yaml

# setup deathstarbench
ansible-playbook -i inventory.yaml -t setup_deathstar playbook-benchmark.yaml
```
## Running benchmarks
Given below are steps on how to setup a scheduler, and how to run a benchmark.
When no scheduler is setup in the cluster, you use the default scheduler. Before setting up another scheduler, remember to remove the existing scheduler.

### Setup Descheduler
```
# setup descheduler
ansible-playbook -i inventory.yaml -t setup_descheduler playbook-schedulers.yaml

# setup descheduler branch: lowNodeUtilization or highNodeUtilization
ansible-playbook -i inventory.yaml -t switch_des_branch -e "branch_name=lowNodeUtilization" playbook-schedulers.yaml

# run descheduler on cluster
ansible-playbook -i inventory.yaml -t run_descheduler playbook-schedulers.yaml
```

### Remove Descheduler
```
# remove descheduler from cluster
ansible-playbook -i inventory.yaml -t remove_descheduler playbook-schedulers.yaml
```

### Setup Poseidon Scheduler
```
# setup poseidon
ansible-playbook -i inventory.yaml -t setup_poseidon playbook-schedulers.yaml

# run poseidon
ansible-playbook -i inentory.yaml -t run_poseidon playbook-schedulers.yaml
```

### Remove Poseidon Scheduler
```
# remove poseidon from cluster
ansible-playbook -i inventory.yaml -t remove_poseidon playbook-schedulers.yaml
```

### Running hotel reservation benchmark
```
# setup hotel reservation
ansible-playbook -i inventory.yaml -t setup_docker playbook-benchmark.yaml
ansible-playbook -i inventory.yaml -t build_image_hotel playbook-benchmark.yaml

# setup hotel reservation branch (do not switch for default)
ansible-playbook -i inventory.yaml -t switch_death_branch -e "branch_name=descheduler" playbook-benchmark.yaml

# run hotel reservation
ansible-playbook -i inventory.yaml -t setup_hotel_reservation playbook-benchmark.yaml

# set up hotel reservation script parameters
cd ../scripts

# example of set parameters in run_workload.sh file
scheduler="descheduler"
algo="hotelReservation"
req_per_sec="100"
node_ip="192.168.138.2" # ip of any node in the cluster
kubernetes_dir="~/DeathStarBench/hotelReservation"
kubernetes_work_dir="/wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua"
duration=20m
setting="lowNodeUtilization" # setting is set only for descheduler, rest is default
thread=50

# setup http route in wrk command in the script
# http://${node_ip}:32767/wrk2-api/review/compose

# run hotel reservation workload
sh run_workload.sh
```

### Remove hotel reservation benchmark
```
# remove pods
ansible-playbook -i inventory.yaml -t remove_hotel_reservation playbook-benchmark.yaml

# delete images
ansible-playbook -i inventory.yaml -t delete_image playbook-benchmark.yaml
```

### Running media microservices benchmark
```
# setup media microservices
ansible-playbook -i inventory.yaml -t setup_docker playbook-benchmark.yaml
ansible-playbook -i inventory.yaml -t build_image_media playbook-benchmark.yaml

# setup media microservices branch
ansible-playbook -i inventory.yaml -t switch_death_branch -e "branch_name=poseidon" playbook-benchmark.yaml

# run media microservices
ansible-playbook -i inventory.yaml -t setup_media_microservices playbook-benchmark.yaml

# set up media microservices script parameters
cd ../scripts

# example of set parameters in run_workload.sh file
scheduler="poseidon"
algo="mediaMicroservices"
req_per_sec="100"
node_ip="192.168.138.2" # ip of any node in the cluster
kubernetes_dir="~/DeathStarBench/mediaMicroservices"
kubernetes_work_dir="/wrk2/scripts/media-microservices/compose-review.lua"
duration=10m
setting="default" # setting is set only for descheduler, rest is default
thread=10

# setup media microservices http route in wrk2 command in the script
# http://localhost:8080/wrk2-api/review/compose

# generate users and movies info
cd ~/DeathStarBench/mediaMicroservices/scripts
python3 write_movie_info.py --server_address 102.168.138.2:8080 && register_users.sh && register_movies.sh

# run media microservices workload
sh run_workload.sh
```

### Remove media microservices benchmark
```
# remove pods
ansible-playbook -i inventory.yaml -t remove_media_microservices playbook-benchmark.yaml

# delete images
ansible-playbook -i inventory.yaml -t delete_image playbook-benchmark.yaml
```

### Running social network benchmark
```
```

### Remove social network benchmark
```
# remove pods
ansible-playbook -i inventory.yaml -t remove_social_network playbook-benchmark.yaml 
```


