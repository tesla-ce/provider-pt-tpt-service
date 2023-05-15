# Compilation Python Wrapper for SIM (v2.89)

## Prerequisites

- setuptools: pip install setuptools


## Compilation

The wrapper compile both, the Python interface and the SIM code

python setup.py build

## Installation

sudo python setup.py install


# How to use

There is an example to test the whole project in the file [test_tpt.py](../src/test_tpt.py).

```python
from sim.sim import SIM

if __name__ == '__main__':
    obj = SIM('c')
    print obj.version()
    print obj.run()
```