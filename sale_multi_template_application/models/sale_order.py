# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("sale_order_template_id")
    def _onchange_sale_order_template_id(self):
        # We need to keep the old lines, to restore them after the template change
        current_lines = self.order_line
        # We need to keep the max sequence
        # of the lines when changing the template
        # because odoo set the sequence for the first line to -99
        max_sequence = max(current_lines.mapped("sequence"), default=10)
        res = super()._onchange_sale_order_template_id()
        for line in self.order_line:
            sequence = 10 if line.sequence == -99 else line.sequence
            line.sequence = sequence + max_sequence
        self.order_line += current_lines
        self.sale_order_template_id = False
        return res
