This module uses the partner_address_version module to create a partner version when confirming a sale order.

By default, this module ensure that the address fields (Invoice Address, Shipping address) are immutable.
This works by ensure that, whenever a sale order is confirmed, the address fields of the sale order will be copied
(and immediately archived), so it will used by this sale order only.
