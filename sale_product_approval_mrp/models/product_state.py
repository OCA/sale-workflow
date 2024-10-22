# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductState(models.Model):
    _inherit = "product.state"

    approved_mrp = fields.Boolean(string="Approved to be Manufactured", default=True)
    approved_component_mrp = fields.Boolean(
        string="Approved to be a Component on a Manufacturing Order", default=True
    )
    approved_bom = fields.Boolean(string="Approved to be on a BoM", default=True)
