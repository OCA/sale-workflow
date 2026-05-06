from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _show_currency_rate_in_report(self):
        """Return True if the informative exchange rate box should be shown.

        Override this method in custom modules to alter the display condition.
        """
        self.ensure_one()
        return self.currency_id != self.company_id.currency_id and bool(
            self.currency_rate
        )
