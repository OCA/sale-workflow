This module allows to have three discounts on every sale order line.

This module overwrites base Odoo's calculation
of the field `untaxed_amount_to_invoice` of the
Sale Order Line to take into account
multiple discount fields instead of hardcoding
the use of only `line.discount`