# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class SaleInvoiceFrequency(models.Model):
    _name = "sale.invoice.frequency"
    _description = "Invoicing frequency for Customers"

    name = fields.Char(
        translate=True,
    )
