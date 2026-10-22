# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2022 Aritz Olea, Landoo SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderCancelReason(models.Model):
    _name = "sale.order.cancel.reason"
    _description = "Sale Order Cancel Reason"

    name = fields.Char(
        required=True,
        translate=True,
    )
