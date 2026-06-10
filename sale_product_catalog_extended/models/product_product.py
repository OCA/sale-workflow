# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    catalog_origin_data = fields.Selection(
        selection=[("sale_order", "Last sales")],
        store=False,
        search="_search_catalog_origin_data",
    )
    catalog_price_mode = fields.Selection(
        selection=[("last_price", "Last sale")],
        store=False,
        search="_search_catalog_price_mode",
    )

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        catalog_orig_data_bool_list = [
            "catalog_origin_data" in subdomain for subdomain in domain
        ]
        if any(catalog_orig_data_bool_list):
            # Get value of catalog_origin_data from domain to know which method throw.
            # Then browse the ids to respect the order.
            product_ids = getattr(
                self,
                f"_get_product_picker_data_{domain[catalog_orig_data_bool_list.index(True)][2]}",
            )()
            # Apply the rest of the catalog filters (category, name, etc.) on top
            # of the products coming from the chosen origin. The catalog_origin_data
            # and catalog_price_mode leaves are no-ops on search, so the original
            # domain can be kept as is while restricting to the origin products.
            matching_ids = set(
                super()
                .search_fetch(
                    expression.AND([domain, [("id", "in", product_ids)]]),
                    field_names,
                )
                .ids
            )
            # Keep the ordering provided by the origin method.
            product_ids = [pid for pid in product_ids if pid in matching_ids]
            return self.browse(product_ids)
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def _search_catalog_origin_data(self, operator, value):
        # Hack to be able to filter by catalog_origin_data
        return []

    @api.model
    def _search_catalog_price_mode(self, operator, value):
        # Display-only field: selecting it does not filter products
        return []

    @api.model
    def _product_picker_data_sale_order_domain(self):
        """Domain to find recent SO lines."""
        months = 6
        start = fields.Datetime.now() - timedelta(days=months * 30)
        start = fields.Datetime.to_string(start)
        catalog_partner_id = self.env.context.get("product_catalog_partner_id", False)
        catalog_order_id = self.env.context.get("product_catalog_order_id", False)
        # Match the history against the delivery address or the commercial
        # partner (with its children) depending on the catalog configuration.
        partner_field = (
            "partner_shipping_id"
            if self.env.context.get("product_catalog_use_delivery_address")
            else "partner_id"
        )
        # Search with sudo for get sale order from other commercials users
        other_sales = (
            self.env["sale.order"]
            # .sudo()
            ._search(
                [
                    ("id", "!=", catalog_order_id),
                    ("company_id", "=", self.env.company.id),
                    (partner_field, "child_of", catalog_partner_id),
                    ("date_order", ">=", start),
                ]
            )
        )
        domain = [
            ("order_id", "in", other_sales),
            ("qty_delivered", "!=", 0.0),
        ]
        return domain

    @api.model
    def _get_product_picker_data_sale_order(self):
        # Specific limit to allow show all products sold in recent orders
        limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_picker.product_picker_last_order_limit", "0")
        )
        found_lines = self.env["sale.order.line"].read_group(
            self._product_picker_data_sale_order_domain(),
            ["product_id", "qty_delivered"],
            ["product_id"],
            lazy=False,
        )
        # Manual ordering that circumvents ORM limitations
        found_lines = sorted(
            found_lines,
            key=lambda res: (
                res["__count"],
                res["qty_delivered"],
            ),
            reverse=True,
        )
        product_ids = [res["product_id"][0] for res in found_lines if res["product_id"]]
        return limit and product_ids[:limit] or product_ids
