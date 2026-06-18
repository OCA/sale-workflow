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
    def _get_catalog_origin_product_ids(self, domain):
        """Return the ordered product ids for the ``catalog_origin_data`` leaf
        found in ``domain`` (e.g. last sales), or ``None`` if the domain has no
        such leaf.

        The ``catalog_origin_data`` field is a display-only filter: its search
        method is a no-op, so the actual restriction to the origin products has
        to be resolved here through the matching ``_get_product_picker_data_*``
        method.
        """
        for leaf in domain:
            if (
                isinstance(leaf, list | tuple)
                and len(leaf) == 3
                and leaf[0] == "catalog_origin_data"
            ):
                method_name = f"_get_product_picker_data_{leaf[2]}"
                # The origin value may be a leftover (e.g. a saved filter or a
                # default) of a module that provided it but is no longer loaded.
                # In that case ignore the origin instead of crashing the catalog.
                if not hasattr(self, method_name):
                    return None
                return getattr(self, method_name)()
        return None

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        # Browse the ids to respect the order given by the origin method.
        product_ids = self._get_catalog_origin_product_ids(domain)
        if product_ids is not None:
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
    def _catalog_origin_search_panel_kwargs(self, kwargs):
        """Restrict the search panel computation (categories, filters and their
        counters) to the products of the selected catalog origin.

        The origin leaf may arrive through any of the search panel domains
        (``search_domain`` for the base search, ``category_domain`` and
        ``filter_domain`` for the other sections). Since its search method is a
        no-op, without this the panel would be computed over the whole catalog
        instead of over the products actually shown for the chosen origin.
        """
        domain = (
            kwargs.get("search_domain", [])
            + kwargs.get("category_domain", [])
            + kwargs.get("filter_domain", [])
        )
        product_ids = self._get_catalog_origin_product_ids(domain)
        if product_ids is None:
            return kwargs
        kwargs = dict(kwargs)
        kwargs["search_domain"] = expression.AND(
            [kwargs.get("search_domain", []), [("id", "in", product_ids)]]
        )
        return kwargs

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        return super().search_panel_select_range(
            field_name, **self._catalog_origin_search_panel_kwargs(kwargs)
        )

    @api.model
    def search_panel_select_multi_range(self, field_name, **kwargs):
        return super().search_panel_select_multi_range(
            field_name, **self._catalog_origin_search_panel_kwargs(kwargs)
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
