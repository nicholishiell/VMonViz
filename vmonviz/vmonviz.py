import datetime

import matplotlib.pyplot as plt
import numpy as np

from pprint import pprint
from rcsdb.connection import session as rcsdb_session
from rcsdb.models import VM, VMLoad, GPULoad, Server

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def vm_to_dict(vm: VM) -> dict:
    server = rcsdb_session.query(Server).filter(Server.hostname==vm.server_hostname).first()

    return {'hostname': vm.hostname,
            'gpu': vm.gpu,
            'gpu_ram': int(server.gpu_ram) if server.gpu_ram is not None else 0,
            'id': vm.id,
            'ip': vm.ip,
            'ram': vm.ram,
            'n_cores': vm.cores,
            'disk_size': vm.root_disk_size}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_vms() -> list[VM]:
    vms = rcsdb_session.query(VM).filter(VM.deleted==None).all()

    vm_list = []

    for vm in vms:
        vm_list.append( vm_to_dict(vm) )

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

def plot_vm_load_data(vm, load_data, show_plot=True):

    timestamps = [i for i,data in enumerate(load_data)]
    loads = [data[1]/100 for data in load_data]
    mem_uses = [data[2] for data in load_data]
    disk_uses = [data[3] for data in load_data]

    x = np.arange(len(timestamps))

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

    # CPU Load subplot
    ax1.set_ylim(0, 1.5)
    ax1.set_ylabel('CPU Load')
    ax1.plot(x, loads, color='tab:blue')
    ax1.set_title('CPU Load')
    ax1.grid(True)

    # Memory Usage subplot
    ax2.set_ylim(0, 1.5)
    ax2.set_ylabel('Memory Percentage Used')
    ax2.plot(x, mem_uses, color='tab:green')
    ax2.set_title('Memory Usage')
    ax2.grid(True)

    # Disk Usage subplot
    ax3.set_ylim(0, 1.5)
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Disk Percentage Used')
    ax3.plot(x, disk_uses, color='tab:red')
    ax3.set_title('Disk Usage')
    ax3.grid(True)

    plt.suptitle(f"VM Load Data for {vm['hostname']}\nRAM: {vm['ram']}GB Disk: {vm['disk_size']}GB Cores: {vm['n_cores']}")
    plt.tight_layout()

    if show_plot:
        plt.savefig(f"./vm_loads/{vm['hostname']}_vm_load.png")
        plt.close()

    return plt

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_gpu_load_data(vm, load_data, show_plot=True):
    timestamps = [i for i, data in enumerate(load_data)]
    core_uses = [data[1]/100 for data in load_data]
    mem_uses = [data[2] for data in load_data]

    x = np.arange(len(timestamps))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # GPU Core Usage subplot
    ax1.set_ylim(0, 1.5)
    ax1.set_ylabel('GPU Core Usage')
    ax1.plot(x, core_uses, color='tab:blue')
    ax1.set_title('GPU Core Usage')
    ax1.grid(True)

    # GPU Memory Usage subplot
    ax2.set_ylim(0, 1.5)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('GPU Memory Usage')
    ax2.plot(x, mem_uses, color='tab:green')
    ax2.set_title('GPU Memory Usage')
    ax2.grid(True)

    plt.suptitle(f"GPU Load Data for {vm['hostname']}")
    plt.tight_layout()

    if show_plot:
        plt.savefig(f"./gpu_loads/{vm['hostname']}_gpu_load.png")
        plt.close()

    return plt

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_vm_load_plot(vm: VM,
                     start_time: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=30)):
    if type(vm) is VM:
        vm = vm_to_dict(vm)

    vm_loads = get_vm_load(vm['id'], start_time)
    vm_load_data = []
    for load in vm_loads:

        mem_percent_used = load.memfree / 1024 / vm['ram']

        disk_percent_used = 1. - load.diskfree / 1024 / vm['disk_size']
        vm_load_data.append( (load.timestamp,
                            load.load,
                            mem_percent_used,
                            disk_percent_used) )


    return plot_vm_load_data(vm, vm_load_data, False)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_gpu_usage_plot(vm: VM,
                       start_time: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=30)):

    if type(vm) is VM:
        vm = vm_to_dict(vm)

    gpu_loads = get_gpu_load(vm['id'], start_time)

    gpu_load_data = []
    for load in gpu_loads:
        gpu_load_data.append( (load.timestamp,
                               load.core_use,
                               load.mem_use) )

    return plot_gpu_load_data(vm, gpu_load_data, False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    vms = get_vms()

    print(f"Found {len(vms)} VMs")
    now = datetime.datetime.now()
    # first_of_month = now.replace(day=1)
    first_of_month = now - datetime.timedelta(days=30)
    print(f"Fetching data since: {first_of_month}")

    for vm in vms:
        print(f"VM ID: {vm['id']}, Hostname: {vm['hostname']}, IP: {vm['ip']}, GPU: {vm['gpu']} GPU-RAM: {vm['gpu_ram']}")

        gpu_load_data = []
        if vm['gpu']:
            gpu_load = get_gpu_load(vm['id'], first_of_month)
            gpu_ram_mb = vm['gpu_ram']*1024

            for load in gpu_load:

                gpu_load_data.append( (load.timestamp,
                                       load.core_use,
                                       load.mem_use/gpu_ram_mb) )


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