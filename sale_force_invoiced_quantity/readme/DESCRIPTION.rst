This module add a new "Force Invoiced" field to sales order lines. This field is used as modifier when computing quantity to be invoiced.

Current behaviour: 

* quantity to invoice = delivered -  invoiced

and

* quantity to invoice = product quantity -  invoiced

Implemented behaviour:

* quantity to invoice = delivered -  invoiced - force invoiced quantity

and 

* quantity to invoice = product quantity -  invoiced - force invoiced quantity