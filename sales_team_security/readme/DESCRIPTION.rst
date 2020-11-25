This module adds a new "Sale" group called "User: Team documents", that
includes the proper permissions for showing only the information related to
that user sale team (having assigned that team/channel or no team at all,
independently from the assigned salesman):

* Contacts.
* Quotations/Sales Orders (implemented in sales_team_security_sale)
* Leads/Opportunities (implemented in sales_team_security_crm)

It also handles the propagation of the sales team from commercial partners to
the contacts, which standard doesn't do.

And finally, there are rules for partners to be restricted to the own ones for
the group "User: Own Documents Only" for being coherent with the permission
scheme. Someone with this permission will see:

- Contacts without salesman nor team assigned.
- Contacts without salesman assigned, but the same team.
- Contacts with them as salesman, independently from the team.
- Contacts with them as follower.
