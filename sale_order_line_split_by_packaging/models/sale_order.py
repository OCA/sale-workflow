from odoo import _, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_split_button = fields.Boolean(compute="_compute_show_split_button")

    def _compute_show_split_button(self):
        for record in self:
            record.show_split_button = False
            if record.product_packaging_id:
                if not record.product_uom_qty % record.product_packaging_id.qty == 0:
                    record.show_split_button = True

    def split_order_line_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Split Order Line"),
            "res_model": "split.order.line.wizard",
            "view_mode": "form",
            "target": "new",
        }
