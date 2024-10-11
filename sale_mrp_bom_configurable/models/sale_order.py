from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    input_config_ids = fields.One2many(
        comodel_name="input.config",
        inverse_name="order_id",
        string="Input configs",
    )

    order_line_count = fields.Integer(
        string="Order lines count", compute="_compute_order_line_count"
    )

    @api.depends("order_line")
    def _compute_order_line_count(self):
        for rec in self:
            rec.order_line_count = len(rec.order_line)

    def show_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Lines",
            "view_mode": "tree",
            "res_model": "sale.order.line",
            "view_id": self.env.ref(
                "sale_mrp_bom_configurable.sale_order_line_tree_multi_edit"
            ).id,
            "domain": [("order_id", "=", self.id), ("is_static_product", "=", False)],
        }
