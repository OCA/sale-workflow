This module adds an optional email template to products.
When a sale is confirmed, a single mail will be sent for each product with the mail template set in the 'Sale confirmation email' (`sale_confirmation_mail_template_id`) field.

This module differs from `product_email_template`, as it sends a mail when an invoice is posted, whereas this module sends a mail when a sale order is confirmed.
As such, depending on your workflow, you may pick either module for the email timing you require.
For instance, if a sale order leads to a contract which generates invoices recurrently, you may prefer to only send a mail when the sale order is confirmed.
