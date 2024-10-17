To use this module, you need to:

1.  Go to *Sales/Configuration/Invoicing frequency* and create your
    custom frequencies.
2.  Set these frequencies in the customer form *Sales and purchases*
    tab.
3.  When a sale is created, the Invoicing frequency of the field
    `partner_id` is propagated.
4.  An user can change Invoicing frequency on sales and customers if has
    group `account.group_account_invoice`.
5.  You can change Invoicing frequency on a sale on the *Other
    information* tab without changing the customer frequency.
6.  When you want to invoice, group sales by Invoicing frequency and
    invoice it.
7.  You can create a CRON for each frequency to automate invoicing
    action.
