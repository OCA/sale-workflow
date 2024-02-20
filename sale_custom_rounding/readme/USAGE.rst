To use this module, you need to:

#. Go to the "Other Information" tab in a sale order to select the rounding method in
   the "Tax Calculation Rounding Method" field. If no option is selected, the rounding
   method set in the company configuration will be applied.
#. If the customer has a value in its "Tax Calculation Rounding Method" field, it will
   be set in the sale order when this contact is selected as the invoice address. This
   option can be changed in the sale order.
#. When multiple sale orders are selected to be invoiced together, the "Tax
   Calculation Rounding Method" is used as a grouping field (i.e. if four sale orders
   are selected, two of them have the "per line" rounding method and the other two
   have the "global rounding" method, two invoices will be generated).
