Others modules provide similar features. The module (sale_order_blanket_order)[https://pypi.org/project/odoo-addon-sale-order-blanket-order] also defines the concept of sale blanket order. The main differences are:

* This module integrates Blanket Orders and Call-Off Orders into the sale.blanket.order object, whereas the other module extends the sale.order object. This means that any extensions made to the sale order model can also apply to blanket orders.

* In the other module, you can deliver and invoice directly from the blanket order. You can also create a separate call-off order to partially deliver the blanket order.
