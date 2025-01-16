The system proposes the **Delivery Lead Time** in sales orders (Other Info tab) based on
the most closely matching lead time profile, determined by the warehouse and delivery
address.

The **Delivery Lead Time** can be manually updated as necessary.

The **Delivery Lead Time** is incorporated into the lead time of each sales order line
by adding days to the lead time proposed based on the standard logic, which governs
delivery scheduling.

Example:
~~~~~~~~

Assume the **Sales Security Lead Time** is set to 2.0 days.

In vanilla Odoo, for a sales order with the following details:

- **Order Date**: 2025-01-19 18:00
- **Order Line Lead Time**: 5.0 days

The delivery order dates would be:

- **Scheduled Date**: 2025-01-22 18:00
- **Deadline**: 2025-01-24 18:00:00

If this module is installed and the **Delivery Lead Time** proposed is 3.0 days, the
values will be updated as follows:

- **Order Line Lead Time**: 8.0 days
- **Deadline (Delivery)**: 2025-01-27 18:00

The **Scheduled Date** will remain unchanged.
