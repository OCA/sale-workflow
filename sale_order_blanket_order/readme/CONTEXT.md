When a company sells the same products to the same customers on a regular basis, it's a common business practice to create a sale framework that defines the terms and conditions of the sales.

If you need a way to define:
* the terms and conditions of the sales,
* the payment terms,
* the delivery terms,

and also secure the quantities of the products to be delivered, the sale framework module is the right choice.

This module introduces 2 new kinkds of sale orders:

1. Blanket Order: This is a sales order that defines the terms and conditions of the sales, the price, the payment terms, the delivery terms, and secures the quantities of the products to be delivered.

2. Call of order: This is a sale order that is created to consume the quantities of the products secured in the sale blanket order.

Others modules can be used to provide the same kind of features. For example, the module (sale_blanket_order)[https://pypi.org/project/odoo-addon-sale-blanket-order] also defines the concept of sale blanket order. The main difference between the two modules is that the sale framework module extends the sale order model to add the sale blanket order and the call of order. This allows to keep the benefits of all the extensions made on the sale order model by other modules without having to adapt them to the sale blanket order model (discount, invoicing; inventory process, ...).
