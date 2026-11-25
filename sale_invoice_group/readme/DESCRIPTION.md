By default, any salesperson who can edit a sales order can also create its
invoices: the sales order to invoice flow creates the `account.move` in `sudo`,
so it is not blocked by the accounting access rights.

When enabled per company, this module restricts that capability to a dedicated
security group, **Invoice Sales Orders**. Users outside the group then get an
error when they try to create invoices from sales orders.

The restriction is disabled by default: installing the module changes nothing
until it is turned on. Sales Administrators and Accounting / Invoicing users
keep the capability; regular salespeople must be granted the group explicitly.
