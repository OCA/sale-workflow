Based on product_customerinfo, this module loads in every
sale order the customer code defined in the product and allows use the
product codes and product name configured in each products in sale
orders.

If a pricelist rule (Discount or Surcharge) computes the price from the
partner prices in the product form, the sale order line takes the price
of the customer. The quantity in the sales order will be proposed from
the minimum quantity defined in the customerinfo.
