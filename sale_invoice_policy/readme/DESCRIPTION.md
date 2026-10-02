This module adds an invoicing policy on sale order level in order to
apply that invoicing policy on the whole sale order.

That invoicing policy can take three values:

- Products Invoicing Policy: The sale order will follow the standard
  behavior and apply the policy depending on products configurations.
- Ordered Quantities: The sale order will invoice the ordered
  quantities.
- Delivered Quantities: The sale order will invoice the delivered
  quantities.

Following the chosen policy, the quantity to invoice and the amount to
invoice on each line will be computed accordingly.

You will be able also to define a default invoicing policy (globally per
company) that can be different than the default invoicing policy for new
products.
