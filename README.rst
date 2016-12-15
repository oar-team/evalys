===============================
Evalys - Overview
===============================

.. image:: https://img.shields.io/pypi/v/evalys.svg
    :target: https://pypi.python.org/pypi/evalys


"Infrastructure Performance Evaluation Toolkit"

It is a data analytics library made to load, compute, and plot data from
job scheduling and resource management traces. It allows scientists and
engineers to extract useful data and visualize it interactively or in an
exported file.

* Free software: BSD license
* Documentation: https://evalys.readthedocs.org.

Features
--------

* Load and all `Batsim <https://github.com/oar-team/batsim>`_ outputs files

  + Compute and plot free slots
  + Simple Gantt visualisation
  + Compute utilisation / queue
  + Compute fragmentation
  + Plot energy and machine state

* Load SWF workload files from `Parallel Workloads Archive
  <http://www.cs.huji.ac.il/labs/parallel/workload/>`_

  + Compute standard scheduling metrics
  + Show job details
  + Extract periods with a given mean utilisation


Examples
--------

You can get a simple example directly by running this::

   cd examples
   ipython --matplotlib qt -i example1.py

You can find a lot of examples in the `./examples` directory.

Gallery
-------

.. image:: _static/jobset_plot.png
.. image:: _static/gantt_comparison.svg

