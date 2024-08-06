vmname=cloud_controller_adaim
vmname2=cloud0_adaim
mount -t "tmpfs tmpfs_${vmname}" "/var/lib/libvirt/scaphandre/${vmname}" -o size=5M
mount -t "tmpfs tmpfs_${vmname2}" "/var/lib/libvirt/scaphandre/${vmname2}" -o size=5M
