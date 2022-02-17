This module adds the field *Priority* in sale order lines and sale orders:
priority of the sale order is computed as the maximum of the priorities of its
lines, setting the priority in the order sets the priority of all its lines
accordingly.

When a picking is created as a result of sale order confirmation,
the created procurement inherits the priority of the order,
then the stock moves and the picking inherit the procurement's priority.
