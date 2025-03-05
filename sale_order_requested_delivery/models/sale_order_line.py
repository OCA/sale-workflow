# Copyright 2024 CamptoCamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    requested_delivery_period_start = fields.Datetime(
        string="Customer Requested Delivery Start Datetime"
    )
    requested_delivery_period_end = fields.Datetime(
        string="Customer Requested Delivery End Datetime"
    )
