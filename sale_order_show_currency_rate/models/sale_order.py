from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _show_currency_rate_in_report(self):
        """Return True if the informative exchange rate box should be shown.

        Override this method in custom modules to alter the display condition.
        """
        self.ensure_one()
        if self.currency_id != self.company_id.currency_id and bool(self.currency_rate):
            return True
        ref_currency = self.company_id.sale_order_currency_report_id
        if not ref_currency or ref_currency == self.company_id.currency_id:
            return False
        date = self.date_order or fields.Date.today()
        return bool(
            self.env["res.currency.rate"].search(
                [
                    ("currency_id", "=", ref_currency.id),
                    ("company_id", "in", (self.company_id.id, False)),
                    ("name", "<=", date),
                ],
                limit=1,
            )
        )

    def _get_report_rate_from_currency(self):
        self.ensure_one()
        ref_currency = self.company_id.sale_order_currency_report_id
        if (
            ref_currency
            and ref_currency != self.company_id.currency_id
            and self.currency_id == self.company_id.currency_id
        ):
            return ref_currency
        return self.currency_id

    def _get_report_display_rate(self):
        self.ensure_one()
        ref_currency = self.company_id.sale_order_currency_report_id
        company_currency = self.company_id.currency_id
        if (
            ref_currency
            and ref_currency != company_currency
            and self.currency_id == company_currency
        ):
            date = self.date_order or fields.Date.today()
            return self.env["res.currency"]._get_conversion_rate(
                ref_currency, company_currency, self.company_id, date
            )
        return (1.0 / self.currency_rate) if self.currency_rate else 0.0
