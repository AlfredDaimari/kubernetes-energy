# Run from benchmark algo directory

scheduler="default"
algo="hotelReservation"
req_per_sec="100"
node_ip="192.168.138.2"
kubernetes_dir="/home/adaim/DeathStarBench/hotelReservation"
kubernetes_work_dir="/wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua" #workload file after work dir
duration=10m

python3 setup_remove_workload.py adaim setup $algo $scheduler $req_per_sec $duration
wrk -D exp -t 10 -c 10 -d $duration -L -s "${kubernetes_dir}${kubernetes_work_dir}" "http://${node_ip}:5000" -R $req_per_sec
python3 setup_remove_workload.py adaim remove $algo $scheduler $rq_per_sec $duration
