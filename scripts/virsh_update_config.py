# edit the vm configuration and add the required configs
import xml.etree.ElementTree as ET
import sys
import subprocess
from time import sleep

vm_domain_name = sys.argv[1]
output_file = sys.argv[2]

def dump_xml():
    with open(output_file, "w") as file:
        subprocess.run(["virsh", "dumpxml", vm_domain_name], stdout=file, stderr=subprocess.PIPE)

def edit_xml():
    tree = ET.parse(output_file)
    root = tree.getroot()  
    
    memoryBacking = ET.Element('memoryBacking')
    source = ET.Element('source',{'type':'memfd'})
    access = ET.Element('access',{'mode':'shared'})
    memoryBacking.append(source)
    memoryBacking.append(access)
    root.append(memoryBacking)

    devices = root.find('devices')
    
    filesystem = ET.Element('filesystem',{'type':'mount', 'accessmode':'passthrough'})
    driver = ET.Element('driver',{'type':'virtiofs'})
    source_fs = ET.Element('source',{'dir':f"/var/lib/libvirt/scaphandre/{vm_domain_name}"})
    target = ET.Element('target',{'dir':f"{vm_domain_name}-scaph"})

    filesystem.append(driver)
    filesystem.append(source_fs)
    filesystem.append(target)
    
    if devices is not None:
        devices.append(filesystem)

    # filesystem json
    filesystem_json = ET.Element('filesystem',{'type':'mount', 'accessmode':'passthrough'})
    driver = ET.Element('driver',{'type':'virtiofs'})
    source_fs = ET.Element('source',{'dir':f"/mnt/sdc/adaim/scaphandre/json"})
    target = ET.Element('target',{'dir':f"{vm_domain_name}-json"})

    filesystem_json.append(driver)
    filesystem_json.append(source_fs)
    filesystem_json.append(target)

    if devices is not None:
        devices.append(filesystem_json)

    tree.write(output_file, encoding='utf-8', xml_declaration=True)


def apply_xml():
    subprocess.run(["virsh", "define", output_file], stdout=subprocess.PIPE)
    print("--Shutting down vm--")
    subprocess.run(["virsh", "shutdown", vm_domain_name], stdout=subprocess.PIPE)
    t = 0 
    while t < 15: 
        print(f"waiting for vm to shutdown - {t}s", end='\r')
        sleep(1)
        t += 1
    print("")
    print("--Starting vm--")
    result = subprocess.run(["virsh", "start", vm_domain_name], capture_output=True)
    print(result.stderr)

def main():
    print(f"--Logging xml of domain {vm_domain_name} to file {output_file}--")
    dump_xml()
    print(f"--Made changes to the xml of domain {vm_domain_name} in file {output_file}--")
    edit_xml()
    print(f"--Updating the xml of domain {vm_domain_name}--")
    apply_xml()

if __name__ == "__main__":
    main()
