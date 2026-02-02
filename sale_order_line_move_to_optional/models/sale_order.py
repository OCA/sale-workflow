from odoo import _, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_values_to_add_to_optional(self):
        self.ensure_one()
        return {
            "order_id": self.order_id.id,
            "price_unit": self.price_unit,
            "name": self.name,
            "product_id": self.product_id.id,
            "quantity": self.product_uom_qty,
            "uom_id": self.product_uom.id,
            "discount": self.discount,
        }

    def move_line_to_optional(self):
        self.ensure_one()

        sale_order = self.order_id

        if sale_order.state not in ["draft", "sent"]:
            raise UserError(_("You cannot add options to a confirmed order."))

        values = self._get_values_to_add_to_optional()
        self.env["sale.order.option"].create(values)
        self.unlink()
