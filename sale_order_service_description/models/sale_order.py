# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT, Nils Coenen
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    service_description = fields.Text(
        string="Service description",
        translate=True,
    )
