###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################

from odoo import _, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def wizard_price_unit_by_margin(self):
        return {
            "name": _("Update Sale Order Line Price by Margin"),
            "type": "ir.actions.act_window",
            "res_model": "recalculate.price.margin",
            "view_mode": "form",
            "target": "new",
            "context": {"default_line_id": self.id},
        }
