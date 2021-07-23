# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    serial_sequence_id = fields.Many2one(
        "ir.sequence", string="Serial Sequence", copy=False
    )
