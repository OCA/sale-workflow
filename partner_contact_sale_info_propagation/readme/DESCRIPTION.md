This module propagates the Salesperson from a company to its contacts.

Odoo already puts the *Salesperson* of the parent company on a contact
when the contact is created under it (or moved to it) and the contact has
no *Salesperson* of its own. This module completes that behavior:

- When the company changes its *Salesperson*, it fills with the same
  *Salesperson* all the contacts that don't have any or that have the
  previous *Salesperson* of the company. The change is propagated down
  the whole contacts hierarchy.
- Contacts having their own, different *Salesperson* are left untouched.
