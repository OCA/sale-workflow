This module adds the possibility for users to force the invoice status of the
sales orders to 'Invoiced', even when not all the quantities ordered or
delivered have been invoiced.

This feature useful in the following scenario:

* The customer disputes the quantities to be invoiced for, after the
  products have been delivered to her/him, and you agree to reduce the
  quantity to invoice (without sending a refund).

* When migrating from a previous Odoo version, in some cases there is less
  quantity invoiced to what was delivered, and you don't want these old sales
  orders to appear in your 'To Invoice' list.
