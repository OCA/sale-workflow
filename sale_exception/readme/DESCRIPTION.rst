This module allows you attach several customizable exceptions to your
sale order in a way that you can filter orders by exceptions type and fix them.

This is especially useful in an scenario for mass sales order import because
it's likely some orders have errors when you import them (like product not
found in Odoo, wrong line format etc.)


When creating or editing Sale Order, configured Exception Rules are checked.
If any is not met, the Sale Order will be blocked
and it won't be possible to "Confirm" it.
