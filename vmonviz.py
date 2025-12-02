import datetime

import matplotlib.pyplot as plt
import numpy as np

from pprint import pprint
from rcsdb.connection import session as rcsdb_session
from rcsdb.models import VM, VMLoad, GPULoad

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_vms() -> list[VM]:
    vms = rcsdb_session.query(VM).filter(VM.deleted==None).all()

    vm_list = []

    for vm in vms:
        vm_list.append({'hostname': vm.hostname,
                       'gpu': vm.gpu,
                       'id': vm.id,
                       'ip': vm.ip,
                       'ram': vm.ram,
                       'n_cores': vm.cores,
                       'disk_size': vm.root_disk_size})

    return vm_list

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_vm_load(vm_id: int, start_time: datetime.datetime) -> list[VMLoad]:
    vm_loads = rcsdb_session.query(VMLoad).filter(  VMLoad.vm_id == vm_id,
                                                    VMLoad.timestamp >= start_time).all()

    return vm_loads

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_gpu_load(vm_id: int, start_time: datetime.datetime) -> list[GPULoad]:
    gpu_loads = rcsdb_session.query(GPULoad).filter(  GPULoad.vm_id == vm_id,
                                                      GPULoad.timestamp >= start_time).all()

    return gpu_loads

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_vm_load_data(vm, load_data):


    timestamps = [i for i,data in enumerate(load_data)]
    loads = [data[1]/100 for data in load_data]
    mem_uses = [data[2] for data in load_data]
    disk_uses = [data[3] for data in load_data]

    x = np.arange(len(timestamps))

    fig, ax1 = plt.subplots()
    ax1.set_ylim(0, 1.5)

    color = 'tab:blue'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Load', color=color)
    ax1.plot(x, loads, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    color = 'tab:green'
    ax1.set_ylabel('Memory Percentage Used', color=color)
    ax1.plot(x, mem_uses, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    color = 'tab:red'
    ax1.spines['right'].set_position(('outward', 60))
    ax1.set_ylabel('Disk Percentage Used', color=color)
    ax1.plot(x, disk_uses, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax1.legend(['CPU Load','Memory %','Disk %'], loc='upper left')

    plt.title(f"VM Load Data for {vm['hostname']}\nRAM: {vm['ram']}GB Disk: {vm['disk_size']}GB Cores: {vm['n_cores']}")

    plt.savefig(f"./vm_loads/{vm['hostname']}_vm_load.png")

    plt.close()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_gpu_load_data(vm, load_data):
    timestamps = [i for i, data in enumerate(load_data)]
    core_uses = [data[1]/100 for data in load_data]
    mem_uses = [data[2]/100 for data in load_data]


    x = np.arange(len(timestamps))

    fig, ax1 = plt.subplots()
    ax1.set_ylim(0, 1.5)

    color = 'tab:blue'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('GPU Core Usage', color=color)
    ax1.plot(x, core_uses, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    color = 'tab:green'
    ax1.set_ylabel('GPU Memory Usage', color=color)
    ax1.plot(x, mem_uses, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax1.legend(['GPU Core %', 'GPU Memory %'], loc='upper left')

    plt.title(f"GPU Load Data for {vm['hostname']}")

    plt.savefig(f"./gpu_loads/{vm['hostname']}_gpu_load.png")

    plt.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    vms = get_vms()
    print(f"Found {len(vms)} VMs")
    now = datetime.datetime.now()
    first_of_month = now.replace(day=1)
    print(f"Fetching data since: {first_of_month}")

    for vm in vms:
        print(f"VM ID: {vm['id']}, Hostname: {vm['hostname']}, IP: {vm['ip']}, GPU: {vm['gpu']}")

        gpu_load_data = []
        if vm['gpu']:
            gpu_load = get_gpu_load(vm['id'], first_of_month)

            for load in gpu_load:
                gpu_load_data.append( (load.timestamp,
                                       load.core_use,
                                       load.mem_use) )

            if len(gpu_load_data) > 0:
                plot_gpu_load_data(vm, gpu_load_data)


        vm_load = get_vm_load(vm['id'], first_of_month)
        vm_load_data = []
        for load in vm_load:

            # I think this was inverted in the original code
            # mem_percent_used = 1. - load.memfree / 1024 / vm['ram']
            mem_percent_used = load.memfree / 1024 / vm['ram']

            disk_percent_used = 1. - load.diskfree / 1024 / vm['disk_size']
            vm_load_data.append( (load.timestamp,
                               load.load,
                               mem_percent_used,
                               disk_percent_used) )

        if len(vm_load_data) > 0:
            plot_vm_load_data(vm, vm_load_data)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
   main()