# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    requested_delivery_period_start = fields.Datetime(
        string="Requested Delivery - Start"
    )
    requested_delivery_period_end = fields.Datetime(string="Requested Delivery - End")
    requested_delivery_period_display = fields.Char(
        string="Requested Delivery Period",
        compute="_compute_requested_delivery_period_display",
    )

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

    @api.depends("requested_delivery_period_start", "requested_delivery_period_end")
    def _compute_requested_delivery_period_display(self):
        lang = self.env["res.lang"]._lang_get(self.env.user.lang or "en_US")
        for rec in self:
            start_date = (
                rec.requested_delivery_period_start.date()
                if rec.requested_delivery_period_start
                else False
            )
            end_date = (
                rec.requested_delivery_period_end.date()
                if rec.requested_delivery_period_end
                else False
            )
            if start_date:
                start_date = start_date.strftime(lang.date_format)
            if end_date:
                end_date = end_date.strftime(lang.date_format)
            if start_date and end_date:
                if (
                    rec.requested_delivery_period_start
                    > rec.requested_delivery_period_end
                ):
                    rec.requested_delivery_period_display = self.env._("INVALID PERIOD")
                    continue
                rec.requested_delivery_period_display = f"{start_date} - {end_date}"
            elif start_date and not end_date:
                rec.requested_delivery_period_display = (
                    self.env._("From %s") % start_date
                )
            elif not start_date and end_date:
                rec.requested_delivery_period_display = (
                    self.env._("Until %s") % end_date
                )
            else:
                rec.requested_delivery_period_display = self.env._("N/A")
