# Copyright 2024 CamptoCamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    requested_delivery_period_start = fields.Datetime(
        string="Requested Delivery - Start"
    )
    requested_delivery_period_end = fields.Datetime(string="Requested Delivery - End")

    @api.constrains("requested_delivery_period_start", "requested_delivery_period_end")
    def _check_requested_delivery_period(self):
        for rec in self:
            if (
                rec.requested_delivery_period_start
                and rec.requested_delivery_period_end
                and rec.requested_delivery_period_start
                > rec.requested_delivery_period_end
            ):
                raise ValidationError(
                    self.env._(
                        "The start of the requested delivery period "
                        "cannot be after the end."
                    )
                )
