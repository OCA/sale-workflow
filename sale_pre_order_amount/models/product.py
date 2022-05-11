from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pre_order_count = fields.Float(
        "Pre-Order Count", compute="_compute_pre_order_count"
    )

    def _compute_pre_order_count(self):
        move_obj = self.env["stock.move"]
        for product_tmpl in self:
            stock_moves = move_obj.search(
                [
                    ("product_id.product_tmpl_id", "=", product_tmpl.id),
                    ("picking_id", "!=", False),
                    ("picking_id.picking_type_id.code", "=", "outgoing"),
                    ("picking_id.state", "in", ["confirmed", "assigned"]),
                ]
            )
            product_tmpl.pre_order_count = sum(stock_moves.mapped("product_uom_qty"))
        return True

    def action_view_pre_order_moves(self):
        stock_moves = self.env["stock.move"].search(
            [
                ("product_id.product_tmpl_id", "=", self.id),
                ("picking_id", "!=", False),
                ("picking_id.picking_type_id.code", "=", "outgoing"),
                ("picking_id.state", "in", ["confirmed", "assigned"]),
            ]
        )
        picking = stock_moves.mapped("picking_id")
        return {
            "name": "Pre-Orders",
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_type": "form",
            "view_mode": "tree,form",
            "views": [
                (self.env.ref("stock.vpicktree").id, "tree"),
                (self.env.ref("stock.view_picking_form").id, "form"),
            ],
            "domain": [("id", "in", picking.ids)],
        }
