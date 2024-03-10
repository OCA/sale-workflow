# Copyright 2022 C2i Change 2 improve <soporte@c2i.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    date_order = fields.Datetime(readonly=False)
