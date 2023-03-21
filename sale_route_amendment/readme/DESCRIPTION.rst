By default into odoo, when a route is modified on a sale order line,
this doesn't impact the existing moves already created and don't replay
the procurement rules

Once this addon is installed, when a route is modified on a sale order
line, the related existing moves are cancelled and the procurement rules
are replayed. This is only possible if nothing has been already begun
in stock for the given line. Otherwise, a user error is raised.
