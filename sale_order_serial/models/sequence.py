# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Sequence(models.Model):
    _inherit = "ir.sequence"

    product_serial_ok = fields.Boolean(string="Product Serials")
