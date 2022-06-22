* Odoo allows to define product.packaging records with a qty = 0. This does not
  make much sense with the can_be_sold checkbox, and we probably need to add a
  constraint here.
