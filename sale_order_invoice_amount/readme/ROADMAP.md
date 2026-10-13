In version 17 of this module and earlier ones, the `amount_invoiced` and
`amount_to_invoice` fields were added to the sale order model as new computed
fields.

Since version 18, these fields are provided directly by Odoo, but they remain
hidden in the interface, so this module now focuses on displaying them in the
sale order views.