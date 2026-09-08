This module lets you define the territory of each sales team as a set of
countries and/or states, and assigns partners to the matching team and
salesperson automatically based on their address.

Since Odoo 18 partners no longer have a *Sales Team* field in the core.
This module adds it back as a computed field:

- A partner whose state belongs to a team territory is assigned to that team.
- Otherwise, a partner whose country belongs to a team territory is assigned
  to that team.
- Contacts without a matching territory take the team of their parent.
- When a partner has no salesperson, the team leader is set as salesperson.

The rest of the sales flow (quotations, invoices, sales analysis) takes the
team from the salesperson as usual, so no other module needs to be modified.
