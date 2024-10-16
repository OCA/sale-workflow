# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _show_cancel_wizard(self):
        if (
            self.env.company.disable_sale_order_cancel_warning
            or config["test_enable"]
            and not self.env.context.get("test_sale_order_cancel_wizard_optional")
        ):
            return super()._show_cancel_wizard()
        return False
