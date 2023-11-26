# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.osv import expression


class StockReturnRequest(models.Model):
    _inherit = "stock.return.request"

    filter_sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="stock_return_request_so_filter",
        string="Selected order(s)",
        copy=False,
        domain=[("state", "in", ["sale", "done"])],
    )
    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Involved Sales",
        readonly=True,
        copy=False,
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_sale_stock_return_request(self):
        self.filter_sale_order_ids = self.filter_sale_order_ids.filtered(
            lambda x: x.partner_id == self.partner_id
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
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        action["context"] = {}
        sales = self.mapped("sale_order_ids")
        if not sales or len(sales) > 1:
            # Sort ids so we can confidently test the string
            action["domain"] = "[('id', 'in', %s)]" % (sorted(sales.ids))
        elif len(sales) == 1:
            res = self.env.ref("sale.view_order_form", False)
            action["views"] = [(res and res.id or False, "form")]
            action["res_id"] = sales.id
        return action


class StockReturnRequestLine(models.Model):
    _inherit = "stock.return.request.line"

    def _get_moves_domain(self):
        domain = super()._get_moves_domain()
        if self.request_id.filter_sale_order_ids:
            domain = expression.AND(
                [
                    domain,
                    [
                        (
                            "sale_line_id.order_id",
                            "in",
                            self.request_id.filter_sale_order_ids.ids,
                        )
                    ],
                ]
            )
        return domain
