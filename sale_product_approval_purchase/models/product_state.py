# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductState(models.Model):
    _inherit = "product.state"

    approved_purchase = fields.Boolean(string="Approved to be Purchased", default=True)
