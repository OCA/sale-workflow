The method _create_invoices in sale module is too complex (E741)
and some parts cannot be avoided when calling super()

This modules does nothing by itself,
only allows to modify some parts. So far it adds:

- Method to modify down payment roundings
