# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Migration note 17.0: rename field to sale_auto_assign_carrier_on_confirm
    # and integrate sale_auto_assign_carier_on_create from
    # delivery_auto_refresh module in OCA/delivery-carrier
    carrier_auto_assign = fields.Boolean()
