## 19.0.1.0.0

- The *Sales Team* propagation has been removed, as the `team_id` field
  no longer exists in contacts since Odoo 18.0. The sales team of a sale
  order is now derived from its salesperson, so propagating the
  *Salesperson* is enough.
