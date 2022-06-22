To use this, you have to configure a few things:

- You may configure the cutoff by either:

  - setting the order cutoff preference to `warehouse_cutoff`,
    in order to use the warehouse cutoff.
  - setting the order cutoff preference to `partner_cutoff`,
    in order to use the partner cutoff.

- By default, customer's delivery window is set to `anytime` (default odoo behavior).
  It can also be set to `working days` or `time window`.
  If the latter is chosen, then time windows will have to be configured on the
  customer.

- By default, warehouse working hours aren't taken into account
  when computing the scheduled date. If you want to use this feature, just
  add a calendar on the warehouse, and enable the `apply cutoff` option.
