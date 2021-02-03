This module adds a new group called "Channel manager", that includes
the proper permissions for showing only the information related to that
channel (having assigned that channel/team or no channel at all, independently
from the assigned salesman):

* Leads/Opportunities
* Contacts.
* Quotations/Sales Orders

It also handles the propagation of the sales team from commercial partners to
the contacts, which standard doesn't do.

It also handles the sync (auto-creation and remove) of followers in company partners
and childs of them according to salesmans. Any example about it:
- Partner company > Salesman: Admin
- Partner company, Contact 1 > Without salesman
- Partner company, Contact 2 > Salesman: Demo
All these partners have these followers: Admin + Demo

And finally, there are rules for partners to be restricted to the own ones for
the group "User: Own Documents Only" for being coherent with the permission
scheme. Someone with this permission will see:

- Contacts without salesman nor channel assigned.
- Contacts without salesman assigned, but the same channel.
- Contacts with them as salesman, independently from the channel.
- Contacts with them as follower.

For keeping consistent accesses, followers of the main and shipping/invoice
contacts are synced according the salesman of the children contacts
