Odoo way of handling sale orders has only 4 states (draft, sent, sale, cancel).

Also, on all services sale orders (linked to timesheets), it only checks if the sale order is in state sale.
In projects, it works fine, but it can lead to errors on users, because they are not allowed to "close" an existing sale order.

The concept of this module is to add a new flag that will detected "finished sale orders" and will not allow to select them anymore.
