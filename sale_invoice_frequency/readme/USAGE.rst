To use this module, you need to:

#. Go to *Sales/Configuration/Invoicing frequency* and create your custom
   frequencies.
#. Set these frequencies in the customer form *Sales and purchases* tab.
#. When a sale is created, the Invoicing frequency of the field ``partner_id``
   is propagated.
#. An user can change Invoicing frequency on sales and customers if has group
   ``account.group_account_invoice``.
#. You can change Invoicing frequency on a sale on the *Other information* tab
   without changing the customer frequency.
#. When you want to invoice, group sales by Invoicing frequency and invoice it.
#. You can create a CRON for each frequency to automate invoicing action.
