# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockReturnRequest(models.Model):
    _inherit = "stock.return.request"

    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Involved Sales",
        readonly=True,
        copy=False,
    )

    def _prepare_move_default_values(self, line, qty, move):
        """Extend this method to add values to return move"""
        vals = super()._prepare_move_default_values(line, qty, move)
        vals.update({"sale_line_id": move.sale_line_id.id})
        return vals

    def _action_confirm(self):
        res = super()._action_confirm()
        if self.state == "confirmed":
            self.sale_order_ids = self.returned_picking_ids.mapped("sale_id")
        return res

    def action_view_sales(self):
        """Display returned sales"""
        action = self.env.ref("sale.action_orders")
        result = action.read()[0]
        result["context"] = {}
        sales = self.mapped("sale_order_ids")
        if not sales or len(sales) > 1:
            # Sort ids so we can confidently test the string
            result["domain"] = "[('id', 'in', %s)]" % (sorted(sales.ids))
        elif len(sales) == 1:
            res = self.env.ref("sale.view_order_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = sales.id
        return result
