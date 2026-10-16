This module is the glue between *Sale Partner Sale Contact* and the
eCommerce (`website_sale`).

When a portal user who is a contact person of a company places an order on
the website, the order is created with the contact person as customer
(`partner_id`).  The auto-switch logic of *Sale Partner Sale Contact* is
implemented as an onchange and therefore never runs for website orders.

This module applies the switch when the website order is confirmed:

* `partner_id` is replaced by the commercial partner (the company);
* the contact person who placed the order is stored in the *Sale Contact*
  field (`sale_contact_partner_id`);
* the invoice and delivery addresses chosen during checkout, the fiscal
  position and the payment terms are preserved.

The switch is deliberately not applied while the order is still a cart:
`website_sale` resets the cart customer to the logged-in user's partner on
every request and looks up abandoned carts by that partner, so an earlier
switch would be reverted and would break cart recovery.
