This module adds a default incoterm address field on the Sales tab of
the partner form, next to the incoterm provided by Odoo.

A different incoterm address can be set per contact within the same
company.

When the partner is selected on a new quotation, or a quotation is
created by code, the incoterm address is retrieved from the partner
record. It can still be changed on the quotation.

Since Odoo 20.0, the default sales incoterm per customer is provided by
the standard `sale` module (`Incoterm` field on the partner). This
module no longer adds its own default incoterm field; existing values
are moved to the standard field on upgrade.
