This module adds a new group called "Channel manager", that includes
the proper permissions for showing only the information related to that
channel:

* Leads/Opportunities
* Customers
* Quotations/Sales Orders

It also handles the propagation of the sales team from commercial partners to
the contacts, which standard doesn't do.

And finally, there are rules for partners to be restricted to the own ones for
the group "User: Own Documents Only" for being coherent with the permission
scheme.

REMARK: partner restrictions won't work unless you touch in the DB an existing
record rule. See more details in Know issues section.
