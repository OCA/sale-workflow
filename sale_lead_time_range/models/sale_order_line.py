# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    customer_lead_range_value = fields.Float(
        "Lead Time",
        default=0,
        help="Time between the order confirmation and "
        "the shipping of the products to the customer",
        inverse="_inverse_customer_lead_range_value",
    )

    customer_lead_range_type = fields.Selection(
        [
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        string="LT Range",
        default="days",
        inverse="_inverse_customer_lead_range_value",
    )

    @api.onchange("customer_lead_range_value", "customer_lead_range_type")
    def _inverse_customer_lead_range_value(self):
        for record in self:
            if record.customer_lead_range_value and record.customer_lead_range_type:
                if record.customer_lead_range_type == "years":
                    today = datetime.now().date()
                    future_date = today + relativedelta(
                        years=record.customer_lead_range_value
                    )
                    record.customer_lead = (future_date - today).days
                elif record.customer_lead_range_type == "months":
                    record.customer_lead = record.customer_lead_range_value * 30
                    today = datetime.now().date()
                    future_date = today + relativedelta(
                        months=record.customer_lead_range_value
                    )
                    record.customer_lead = (future_date - today).days
                elif record.customer_lead_range_type == "weeks":
                    record.customer_lead = record.customer_lead_range_value * 7
                elif record.customer_lead_range_type == "days":
                    record.customer_lead = record.customer_lead_range_value

    @api.onchange("product_id")
    def _onchange_product_id_set_customer_lead(self):
        res = super()._onchange_product_id_set_customer_lead()
        self.update(
            {
                "customer_lead_range_value": self.product_id.sale_delay_range_value,
                "customer_lead_range_type": self.product_id.sale_delay_range_type,
            }
        )
        return res
