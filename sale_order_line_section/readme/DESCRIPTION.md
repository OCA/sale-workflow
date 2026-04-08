This module adds a stored Section field on sale order lines.

In standard Odoo, the relation between a line and its section is only implicit:
a line belongs to the nearest previous section according to the order sequence.
This is inconvenient for domains, grouping, reporting, or custom business logic
because there is no direct field to use.

With this module, each non-section sale order line is linked to its nearest
previous section line.

Typical use cases include:

- grouping sale order lines by section in tree views, exports, or reports;
- filtering all lines that belong to a given section without recomputing the
  relation from the sequence;
