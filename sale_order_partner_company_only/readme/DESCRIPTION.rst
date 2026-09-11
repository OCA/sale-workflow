This module restricts the partner selection in sale orders to companies only
(partners with ``is_company = True``).

Individual contacts cannot be selected as the main customer/partner on sale
orders.

This module is used by ``sale_partner_sale_contact`` (available in the
sale-workflow repository) to enforce proper commercial relationships while
allowing contact person tracking.
