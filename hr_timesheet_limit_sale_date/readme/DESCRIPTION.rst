This module adds a date field to sale order and invoice. This date is limitation
selection of timesheet lines for including them in sale order and invoice.
When create an invoice limit date will be inherited from sale order, then date
in sale order is cleanups, when invoice validated lines will be constraint by
limitation date.
Known issues if sale order has two invoices in draft state, and the validated 
one with the newest date or without date that it pick all lines till this date, 
and invoice with older date will have no any lines.
