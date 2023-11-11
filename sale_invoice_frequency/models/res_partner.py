# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_frequency_id = fields.Many2one(
        comodel_name="sale.invoice.frequency",
        string="Invoicing frequency",
        help="Invoicing frequency for this customer",
    )
