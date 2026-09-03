This module will not trigger the recomputation of the lines attributes when installing only this module.
This will avoid the installation timeout.

If you later want to recompute the lines, you can use a scheduled action similar to this one:

```python
env["sale.order.line"].search([
  ("product_template_id.attribute_line_ids", "!=", []),
])._compute_all_product_template_attribute_value_ids()
```
