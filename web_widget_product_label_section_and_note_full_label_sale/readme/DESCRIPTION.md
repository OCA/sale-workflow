Glue module between ``web_widget_product_label_section_and_note_full_label``
and the ``sale`` module, since the original widget is extended in the sale
module and therefore needs some special customizations to work for sale order
lines.

In addition to the above, this module will force reuse of name from sale
order line on account move line when creating invoice from sale order.

