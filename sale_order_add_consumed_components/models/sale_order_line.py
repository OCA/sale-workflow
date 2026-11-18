# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_mrp_component_line = fields.Boolean("Added from MO Component", default=False)

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Skip stock rule launch for MRP component lines - they represent
        # already-consumed materials, not new procurement needs.
        lines = self.filtered(lambda ln: not ln.is_mrp_component_line)
        if not lines:
            return True
        return super(SaleOrderLine, lines)._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
