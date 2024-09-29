scheduler="default"
algo="hotelReservation"
python3 setup_remove_workload.py adaim setup $algo $scheduler
# run workload
python3 setup_remove_workload.py adaim remove $algo $scheduler
