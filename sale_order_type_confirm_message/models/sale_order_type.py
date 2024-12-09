# Copyright 2021 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderTypology(models.Model):
    _inherit = "sale.order.type"

    has_confirmation_message = fields.Boolean()
    confirmation_message = fields.Text(
        translate=True,
    )
