# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import datetime, safe_eval


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Allowed Products",
        compute="_compute_product_assortment_ids",
    )
    has_allowed_products = fields.Boolean(compute="_compute_product_assortment_ids")

    @api.depends("partner_id", "partner_shipping_id", "partner_invoice_id")
    def _compute_product_assortment_ids(self):
        self.allowed_product_ids = False
        self.has_allowed_products = False
        partner_field = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_assortment.partner_field", "partner_id")
        )
        product_domain = []
        if self[partner_field]:
            filters_partner_domain = self.env["ir.filters"].search(
                [("is_assortment", "=", True)]
            )
            filters_partner_domain = filters_partner_domain.filtered(
                lambda x: x.all_partner_ids & self[partner_field]
            )
            if filters_partner_domain:
                # use OR to combine allowed products
                # and negate the blacklisted ones with AND
                eval_product_domain = expression.OR(
                    safe_eval(
                        domain,
                        {"datetime": datetime, "context_today": datetime.datetime.now},
                    )
                    for domain in filters_partner_domain.mapped("domain")
                )
                whitelist_product_domain = expression.OR(
                    [
                        eval_product_domain,
                        [
                            (
                                "id",
                                "in",
                                filters_partner_domain.mapped(
                                    "whitelist_product_ids.id"
                                ),
                            )
                        ],
                    ]
                )
                blacklist_product_domain = [
                    (
                        "id",
                        "not in",
                        filters_partner_domain.mapped("blacklist_product_ids.id"),
                    )
                ]
                product_domain = expression.AND(
                    [whitelist_product_domain, blacklist_product_domain]
                )
            if product_domain:
                self.allowed_product_ids = self.env["product.product"].search(
                    product_domain
                )
            if self.allowed_product_ids:
                self.has_allowed_products = True

    @api.onchange("partner_id", "partner_shipping_id", "partner_invoice_id")
    def _onchange_partner_id(self):
        """
        Check if all the products in the order lines
        contains products that are allowed for the partner
        """
        for order in self:
            if order.has_allowed_products:
                product_ids = order.order_line.mapped("product_id")
                products_set = set(product_ids.ids)
                allowed_products_set = set(order.allowed_product_ids.ids)
                if not products_set <= allowed_products_set:
                    products_not_allowed_set = products_set - allowed_products_set
                    raise UserError(
                        _(
                            "This SO contains one or more products "
                            "that are not allowed for partner %s:\n- %s"
                        )
                        % (
                            order.partner_id.name,
                            "\n- ".join(
                                self.env["product.product"]
                                .browse(products_not_allowed_set)
                                .mapped("name")
                            ),
                        )
                    )
