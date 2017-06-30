Meh?
====

This directory contains several
[asymptote](http://asymptote.sourceforge.net/) files, which generate
PDF figures.

List of asymptote files
=======================

- [job.asy](./job.asy): Job structure, base drawing functions
  (jobs, gantt chart axes)
- [job_figures.asy](./job_figures.asy): figures about a job definition and
  some metrics (waiting time, turnaround time...)
- [easy_bf.asy](./easy_bf.asy): Some steps of a simple execution of
  FCFS + aggressive backfilling
  (with 1 priority job that should not be delayed)
- [gantt_examples.asy](./gantt_examples.asy): Gantt charts resulting from
  different energy management policies
- [llh.asy](./llh.asy): Visualisation of the Liquid Load Horizon
  (online estimator of the system unresponsiveness)

How to generate the figures?
============================

Install asymptote if needed, then simply call ``make pdf`` (or ``make png``).

Install asymptote on Arch-based systems: ``pacman -S asymptote``.
Install asymptote on debian-based systems: ``apt-get install asymptote``.
Sources on [github](https://github.com/vectorgraphics/asymptote).

Gallery
=======
Rasterized images can be found [there](./png).
Please notice that the rasterization process made the images ugly, classical
output is better ;).
