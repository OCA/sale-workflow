This module adds a commercial semaphore to help sales teams assess
whether a quoted price stays within the discount policy defined for a
product or product category.

For each product you can define three discount thresholds, expressed as
a percentage over the public sale price:

- **Green**: price is within the preferred commercial margin.
- **Yellow**: price is still acceptable, but already close to the limit.
- **Red**: price is below the warning threshold and should be reviewed.

The semaphore is displayed directly on sales order lines and propagated
to customer invoice lines and reporting models, so the same visual
indicator is available during the full sales flow.

When no product-specific configuration exists, the module can also reuse
the thresholds defined on the product category.
