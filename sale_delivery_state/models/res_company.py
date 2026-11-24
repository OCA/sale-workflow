# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    skip_service_sale_delivery_state = fields.Boolean(
        string="Skip Service products for Sale Delivery State"
    )
