It adds a new group 'can modify credit limit', only users with this group are allowed to change credit limit on partners.
It also adds an exception to check that you can not aproove sale orders that would exceed credit limit. It checks:

* The current due of the partner
* The amount of Sale Orders aproved but not yet invoiced
* The invoices in draft state.
* The amount of the Sale Order to be aproved and compares it with the credit limit of the partner. If the credit limit is below this, then it is not to approve the Sale Order.
