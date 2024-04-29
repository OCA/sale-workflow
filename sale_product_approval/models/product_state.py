# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductState(models.Model):
    _inherit = "product.state"

    approved_sale = fields.Boolean(string="Approved to be added to SO", default=True)
    approved_sale_confirm = fields.Boolean(string="Approved to be Sold", default=True)
