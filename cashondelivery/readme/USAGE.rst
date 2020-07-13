To use this add-on we must do the following:

#. Go to Accounting> Configuration> Payment methods and edit the payment method (s) to define the field "Is it cash delivery?" a truth
#. We will define a minimum amount for cash on delivery (validate before confirming the sales order)

When a sales order that has the cash delivery payment method is confirmed, it is checked if the total_cashondelivery field of the sales order has a correct amount.
The total_cashondelivery amount is taken to the picking generated when confirming the sales order
