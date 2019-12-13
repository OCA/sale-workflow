This modules allows to define an automatic workflow to a Sale Order when a
payment transaction is created for it (to manage automatic invoice creation or
...).

Then, when the transaction is done, let the Odoo standard process flow
to create corresponding payments and reconciliation. The cron job is located
as usual in Settings > Technical Settings > Automation > Scheduled Actions >
'Post process payment transactions' and is active by default.
