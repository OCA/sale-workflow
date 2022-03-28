# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    uom_category_id = fields.Many2one(
        related="uom_id.category_id", store=False, readonly=True
    )
    sale_order_partner_id_product = fields.Boolean(
        compute="_compute_sale_order_partner_id_product",
        search="_search_sale_order_partner_id_product",
        readonly=True,
    )
    categ_name = fields.Char(
        related="categ_id.name", string="Category name", store=False, readonly=True
    )
    categ_parent_path = fields.Char(
        related="categ_id.parent_path", store=False, readonly=True
    )

    def _compute_sale_order_partner_id_product(self):
        """Void response as we're just interested in the search part"""
        self.sale_order_partner_id_product = False
        return False

    def _search_sale_order_partner_id_product(self, operator, value):
        """Given the proper context we'll return the proper ids related to
        the partner sale orders and search criterias"""
        context = self.env.context
        if context.get("active_search_group_name") == "product_history_shipping":
            partner_id = self.env.context.get("sale_order_partner_shipping_id")
            partner = self.env["res.partner"].browse(partner_id)
        else:
            partner_id = self.env.context.get("sale_order_partner_id")
            partner = self.env["res.partner"].browse(partner_id)
            partner = partner.commercial_partner_id
        if not partner or operator not in ["=", "!="]:
            return []
        orders = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_id", "child_of", partner.id),
                    (
                        "date_order",
                        ">=",
                        fields.Datetime.now() - relativedelta(months=13),
                    ),
                ]
            )
        )
        lines = (
            self.env["sale.order.line"]
            .sudo()
            .search_read(
                [("order_id", "in", orders.ids), ("state", "in", ["sale", "done"])],
                ["product_id"],
                order="id DESC, sequence DESC",
            )
        )
        products_domain = [x["product_id"][0] for x in lines if x["product_id"]] or [0]
        operator = "in" if operator == "=" else "not in"
        return [("id", operator, products_domain)]
