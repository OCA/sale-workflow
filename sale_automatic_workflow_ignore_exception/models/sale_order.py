# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm(self):
        if self.env.context.get("ignore_exception_when_confirm"):
            self.write({"ignore_exception": True})
        return super().action_confirm()
