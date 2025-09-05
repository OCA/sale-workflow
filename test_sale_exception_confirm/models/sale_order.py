# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    before_confirm = fields.Char()
    after_confirm = fields.Char()

    def action_confirm(self):
        self.write({"before_confirm": "Write before confirm"})
        res = super().action_confirm()
        self.write({"after_confirm": "Write after confirm"})
        return res
