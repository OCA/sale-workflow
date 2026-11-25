When a down payment exceeds the value of a partial delivery, Odoo
normally generates a credit note with a negative quantity. This module
adds two alternatives in the *Create Invoice* wizard:

- **Proportional**: deducts the share of the down payment matching the
  delivery ratio.
- **Fixed amount**: deducts a manually entered amount (bounded between 0
  and the total DP).
