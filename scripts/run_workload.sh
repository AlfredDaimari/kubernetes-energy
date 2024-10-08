# Run from benchmark algo directory

scheduler="default"
algo="hotelReservation"
req_per_sec="100"
node_ip="192.168.138.2"

python3 setup_remove_workload.py adaim setup $algo $scheduler $req_per_sec
wrk -D exp -t 10 -c 10 -d 10m -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua "http://${node_ip}:5000" -R $req_per_sec
python3 setup_remove_workload.py adaim remove $algo $scheduler $rq_per_sec
