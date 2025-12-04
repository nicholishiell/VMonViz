# VMonViz

VM Monitoring Visualization Tool for RCS Cloud Infrastructure

## Installation

Install the package using pip:

```bash
pip install -e .
```

Or install from the parent directory:

```bash
pip install -e VMon/VMonViz
```

## Usage

After installation, you can run the tool using:

```bash
vmonviz
```

Or use it programmatically in Python:

```python
from vmonviz import get_vms, plot_vm_load_data, plot_gpu_load_data
import datetime

# Get all VMs
vms = get_vms()

# Generate plots for the last 30 days
start_time = datetime.datetime.now() - datetime.timedelta(days=30)
# ... use the functions as needed
```

## Dependencies

- matplotlib
- numpy
- rcsdb

## Features

- Fetch VM and GPU load data from the RCS database
- Generate CPU load, memory usage, and disk usage plots for VMs
- Generate GPU core and memory usage plots for GPU-enabled VMs
- Automatically save plots to `vm_loads/` and `gpu_loads/` directories
