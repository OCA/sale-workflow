# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Display-only search panel fields. Their default can be set as any other
    # field through Default Values (ir.default), also from the Sales settings.
    # Cards shown by the catalog: the products when empty, or the ones other
    # modules add (e.g. the vendor cards of sale_product_catalog_supplierinfo)
    # through their ``_get_product_picker_data_<key>`` method.
    catalog_origin_data = fields.Selection(
        selection=[],
        store=False,
        search="_search_catalog_origin_data",
    )
    # Restrict the origin products to the ones sold to the customer in the
    # last days, most frequently sold first.
    catalog_last_sales = fields.Selection(
        selection=[("last_sales", "Last sales")],
        store=False,
        search="_search_catalog_last_sales",
    )
    catalog_price_mode = fields.Selection(
        selection=[("last_price", "Last sale")],
        store=False,
        search="_search_catalog_price_mode",
    )
    # Partner the sale history is matched against: the commercial partner when
    # empty, or the delivery address.
    catalog_history_partner = fields.Selection(
        selection=[("delivery_address", "Delivery address")],
        store=False,
        search="_search_catalog_history_partner",
    )

    @api.model
    def _get_catalog_origin_product_ids(self, domain):
        """Return the ordered product ids for the ``catalog_origin_data`` and
        ``catalog_last_sales`` leaves found in ``domain``, or ``None`` if the
        domain has none of them.

        Both fields are display-only filters: their search method is a no-op,
        so the actual restriction is resolved here. The origin products come
        from the matching ``_get_product_picker_data_*`` method and, with the
        last sales option, only the ones sold to the customer are kept, most
        frequently sold first.
        """
        values = {
            leaf[0]: leaf[2]
            for leaf in domain
            if isinstance(leaf, list | tuple) and len(leaf) == 3
        }
        products = self.with_context(
            product_catalog_use_delivery_address=(
                values.get("catalog_history_partner") == "delivery_address"
            )
        )
        product_ids = None
        origin = values.get("catalog_origin_data")
        # The origin value may be a leftover (e.g. a saved filter or a default)
        # of a module that provided it but is no longer loaded. In that case
        # ignore the origin instead of crashing the catalog.
        method_name = f"_get_product_picker_data_{origin}"
        if origin and hasattr(products, method_name):
            product_ids = getattr(products, method_name)()
        if values.get("catalog_last_sales") != "last_sales":
            return product_ids
        sold_ids = products._get_catalog_last_sales_product_ids()
        if product_ids is not None:
            origin_ids = set(product_ids)
            sold_ids = [pid for pid in sold_ids if pid in origin_ids]
        # Applied after combining with the origin, so it limits the products
        # actually shown.
        limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_product_catalog_extended.catalog_last_order_limit", "0")
        )
        return sold_ids[:limit] if limit else sold_ids

    @api.model
    def _search_catalog_origin_ids(self, domain):
        """Return the ordered ids of the products of the catalog origin found in
        ``domain`` that also match the rest of its leaves, or ``None`` if the
        domain has no origin leaf.
        """
        product_ids = self._get_catalog_origin_product_ids(domain)
        if product_ids is None:
            return None
        # Apply the rest of the catalog filters (category, name, etc.) on top
        # of the products coming from the chosen origin. The catalog_origin_data
        # and catalog_price_mode leaves are no-ops on search, so the original
        # domain can be kept as is while restricting to the origin products.
        # Use _search, as search() goes through search_fetch() again.
        matching_ids = set(
            self._search(
                expression.AND([domain, [("id", "in", product_ids)]])
            ).get_result_ids()
        )
        # Keep the ordering provided by the origin method.
        return [pid for pid in product_ids if pid in matching_ids]

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        product_ids = self._search_catalog_origin_ids(domain)
        if product_ids is not None:
            # Paginate over the origin ordering, as the kanban view loads the
            # records page by page.
            end = offset + limit if limit else None
            return self.browse(product_ids[offset:end])
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def search_count(self, domain, limit=None):
        # The pager counts the records with the same domain, so it must be
        # restricted to the origin products too.
        product_ids = self._search_catalog_origin_ids(domain)
        if product_ids is not None:
            return min(len(product_ids), limit) if limit else len(product_ids)
        return super().search_count(domain, limit=limit)

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
    def _search_catalog_last_sales(self, operator, value):
        # Display-only field: resolved in _get_catalog_origin_product_ids
        return []

    @api.model
    def _search_catalog_price_mode(self, operator, value):
        # Display-only field: selecting it does not filter products
        return []

    @api.model
    def _search_catalog_history_partner(self, operator, value):
        # Display-only field: selecting it does not filter products
        return []

    @api.model
    def _get_catalog_history_partner_id(self):
        """Partner the catalog matches the sale history against, as chosen in
        the ``catalog_history_partner`` search panel section.
        """
        if self.env.context.get("product_catalog_use_delivery_address"):
            return self.env.context.get("product_catalog_shipping_partner_id", False)
        return self.env.context.get("product_catalog_partner_id", False)

    @api.model
    def _product_picker_data_sale_order_domain(self):
        """Domain to find recent SO lines."""
        days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_product_catalog_extended.catalog_last_order_days", "180")
        )
        start = fields.Datetime.now() - timedelta(days=days)
        start = fields.Datetime.to_string(start)
        catalog_partner_id = self._get_catalog_history_partner_id()
        catalog_order_id = self.env.context.get("product_catalog_order_id", False)
        # Match the history against the delivery address or the commercial
        # partner (with its children) depending on the catalog selection.
        partner_field = (
            "partner_shipping_id"
            if self.env.context.get("product_catalog_use_delivery_address")
            else "partner_id"
        )
        # The catalog history must reflect every order of the partner
        # regardless of salesperson, not only the ones assigned to the
        # current user, so this search bypasses the "own documents" rule.
        other_sales = (
            self.env["sale.order"]
            .sudo()
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
    def _get_catalog_excluded_product_ids(self):
        """Products manually excluded from the *Last sales* option for the
        partner the catalog matches the sale history against.

        Exclusions are dropped when the product is sold to that partner again
        (see ``SaleOrder._remove_catalog_last_sales_exclusions``), so this only
        has to read the ones still standing.
        """
        partner_id = self._get_catalog_history_partner_id()
        if not partner_id:
            return set()
        exclusions = self.env["sale.catalog.product.exclusion"].search_read(
            [("partner_id", "=", partner_id)], ["product_id"]
        )
        return {exclusion["product_id"][0] for exclusion in exclusions}

    @api.model
    def _get_catalog_last_sales_product_ids(self):
        """Return the ids of the products sold to the customer in the last
        days, most frequently sold first, then the most delivered quantity.
        """
        # Read the lines with sudo for the same reason as the orders in the
        # domain: the "own documents" rule also applies to sale order lines.
        groups = (
            self.env["sale.order.line"]
            .sudo()
            ._read_group(
                self._product_picker_data_sale_order_domain(),
                groupby=["product_id"],
                aggregates=["__count", "qty_delivered:sum"],
            )
        )
        # Most frequently sold first, then the most delivered quantity
        groups = sorted(groups, key=lambda group: group[1:], reverse=True)
        # Drop the products manually excluded from the last sales, before the
        # limit is applied, so an exclusion frees a slot for the next product.
        excluded_ids = self._get_catalog_excluded_product_ids()
        return [
            product.id
            for product, _count, _qty in groups
            if product and product.id not in excluded_ids
        ]
