# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Used to gate editability in the smart button list/form views the same
    # way the "order_line" field is gated on the sale order form itself
    # (`readonly="state == 'cancel' or locked"`), since these standalone
    # views are not nested inside the sale order form and cannot reach
    # `parent.locked`.
    order_locked = fields.Boolean(related="order_id.locked")
