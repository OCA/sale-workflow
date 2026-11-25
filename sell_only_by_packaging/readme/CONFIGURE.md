Following options are available to define which unit can be sold and
which product can only be sold by packaging.

- Packagings (on the product): the additional units of measure a product
  can be sold by. Only units sharing a common reference with the product
  unit are taken into account.
- Sell only by packaging: On product template model, this checkbox
  restricts sales of these products to their packaging units. A sale
  order line using the product unit itself, or a quantity that is not a
  whole number of packaging units, raises an error. New sale order lines
  default to the smallest packaging unit of the product.
- Force sale quantity (on the packaging unit): force rounds up the
  quantity during creation/modification of the sale order line to a whole
  number of that unit.
