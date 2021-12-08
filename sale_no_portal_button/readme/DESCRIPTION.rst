Odoo Core shoehorns portal functionality into the sale module, which might not be what you want.
Any time you use the chatter on a sale order, an email will be sent to the client (partner_id),
with a button displaying access to this sale order. This module hides that button, and only displays
it for contacts that have a user associated with them
