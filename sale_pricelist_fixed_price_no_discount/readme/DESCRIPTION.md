This module prevents users from applying manual discounts on sale order lines
when the applied pricelist rule uses a fixed price.

The discount field becomes readonly on those sale lines, and backend writes are
validated to block discounts created through imports, RPC calls, or custom code.
