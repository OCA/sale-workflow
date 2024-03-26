This module aims to compute sale delivery dates with respect to warehouse cutoff,
warehouse calendar and the customer delivery preferences (time windows).

Cutoff
------

Potpone order preparation by 1 day if it has been validated after
the partner or the warehouse cutoff.

This can be bypassed if commitment date is set or if no cutoff is set.


Warehouse Calendar
------------------

Plan workload and postpones the delivery according to the warehouse calendar, if any.


Partner delivery window
-----------------------

Allows to define delivery preferences on customers,
in order to select possible delivery windows to postpone deliveries to.
