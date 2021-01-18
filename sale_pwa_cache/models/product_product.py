# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    uom_category_id = fields.Many2one(related="uom_id.category_id", store=False, readonly=True)
    sale_order_partner_id_product = fields.Boolean(
        compute="_compute_sale_order_partner_id_product",
        search="_search_sale_order_partner_id_product",
        readonly=True,
    )

    def _compute_sale_order_partner_id_product(self):
        """Void response as we're just interested in the search part"""
        return

    @api.model
    def _get_parner_lines(self, partner):
        """Get the lines properly ordered"""
        if not partner:
            return []
        if isinstance(partner, int):
            partner = self.env["res.partner"].browse(partner)
        return self.env["sale.order.line"].search_read(
            [
                (
                    "order_id.partner_id",
                    "child_of",
                    partner.commercial_partner_id.id
                ),
                ("state", "in", ["sale", "done"]),
            ],
            ["product_id"],
            order="id DESC, sequence DESC",
        )

    def _search_sale_order_partner_id_product(self, operator, value):
        """Given the proper context we'll return the proper ids related to
        the partner sale orders and search criterias"""
        partner = self.env.context.get("sale_order_partner_id")
        if not partner or operator not in ["=", "!="]:
            return []
        lines = self._get_parner_lines(partner)
        products = [x["product_id"][0] for x in lines] or [0]
        operator = "in" if operator == "=" else "not in"
        return [("id", operator, products)]
