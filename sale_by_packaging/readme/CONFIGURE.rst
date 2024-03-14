Following options are available to define which packaging type can be sold and
which product can only be sold by packaging.

* Can be sold: On product packaging type model, this checkbox defines if product
  packagings from this particular type are available to be selected on sale
  order line.

* Sell only by packaging: On product template model, this checkbox restricts
  sales of these products if no packaging is selected on the sale order line.
  If no packaging is selected, it will either be auto-assigned if the quantity
  on the sale order line matches a packaging quantity or an error will be raised.

* Force sale quantity (on the packaging): force rounds up the quantity during
  creation/modification of the sale order line with the factor set on the packaging.
