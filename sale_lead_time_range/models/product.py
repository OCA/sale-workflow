from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_delay_range_value = fields.Float(
        "Customer Lead Time",
        store=True,
        inverse="_inverse_sale_delay_range_value",
        help="Delivery lead time. It's the time, promised to the customer, "
        "between the confirmation of the sales order and the delivery.",
    )

    sale_delay_range_type = fields.Selection(
        [
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        string="Range type",
        default="days",
        inverse="_inverse_sale_delay_range_value",
    )

    def _inverse_sale_delay_range_value(self):
        for record in self:
            if record.sale_delay_range_value and record.sale_delay_range_type:
                if record.sale_delay_range_type == "years":
                    today = datetime.now().date()
                    future_date = today + relativedelta(
                        years=record.sale_delay_range_value
                    )
                    record.sale_delay = (future_date - today).days
                elif record.sale_delay_range_type == "months":
                    today = datetime.now().date()
                    future_date = today + relativedelta(
                        months=record.sale_delay_range_value
                    )
                    record.sale_delay = (future_date - today).days
                elif record.sale_delay_range_type == "weeks":
                    record.sale_delay = record.sale_delay_range_value * 7
                elif record.sale_delay_range_type == "days":
                    record.sale_delay = record.sale_delay_range_value
