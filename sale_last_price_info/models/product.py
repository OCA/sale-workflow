# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_sale_price = fields.Float(compute="_compute_last_sale")
    last_sale_date = fields.Date(compute="_compute_last_sale")
    last_customer_id = fields.Many2one(
        comodel_name="res.partner", string="Last Customer", compute="_compute_last_sale"
    )

    def _compute_last_sale(self):
        """Get last sale price, last sale date and last customer"""
        for product in self:
            line = self.env["sale.order.line"].search(
                [("product_id", "=", product.id), ("state", "in", ["sale", "done"])],
                limit=1,
                order="date_order_sale_last_price_info desc",
            )
            product.update(
                {
                    "last_sale_date": fields.Datetime.to_string(
                        line.date_order_sale_last_price_info
                    ),
                    "last_sale_price": line.price_unit,
                    "last_customer_id": line.order_id.partner_id,
                }
            )
