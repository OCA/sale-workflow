# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _show_cancel_wizard(self):
        if (
            not self.env.context.get("disable_cancel_warning")
            and self.env.company.enable_sale_cancel_confirmed_invoice
        ):
            return True
        return False
