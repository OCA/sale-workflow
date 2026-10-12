# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_mrp_byproduct_line = fields.Boolean(
        string="Added from MO By-product",
        default=False,
        help="If True, this sale order line was automatically added from a "
        "Manufacturing Order's by-product production and should not trigger "
        "new procurements.",
    )

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        lines_to_procure = self.filtered(lambda line: not line.is_mrp_byproduct_line)
        if not lines_to_procure:
            return True
        return super(SaleOrderLine, lines_to_procure)._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
