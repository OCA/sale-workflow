# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _catalog_history_partner(self, use_delivery_address=False):
        """Partner used to look for the customer sale history in the catalog."""
        self.ensure_one()
        if use_delivery_address:
            return self.partner_shipping_id
        return self.partner_id.commercial_partner_id

    def _get_catalog_history_context(self):
        """Context passed to the catalog domain with the partners the sale
        history can be matched against (see ``catalog_history_partner``).
        """
        return {
            "product_catalog_partner_id": self._catalog_history_partner().id,
            "product_catalog_shipping_partner_id": self._catalog_history_partner(
                use_delivery_address=True
            ).id,
            "product_catalog_order_id": self.id,
        }

    def _get_catalog_last_sale_lines(
        self, product_ids, groupby=("product_id",), use_delivery_address=False
    ):
        """Return ``{group: last sale line}`` of the sale history the catalog
        matches, grouped by ``groupby`` (a tuple of sale order line fields
        starting by ``product_id``), with a single grouped query.

        The lines are read with sudo, as the "own documents" rule also applies
        to sale order lines and the history spans every salesperson.
        """
        if not product_ids:
            return {}
        domain = (
            self.env["product.product"]
            .with_context(
                **self._get_catalog_history_context(),
                product_catalog_use_delivery_address=use_delivery_address,
            )
            ._product_picker_data_sale_order_domain()
        )
        domain += [("product_id", "in", product_ids)]
        sol_model = self.env["sale.order.line"].sudo()
        groups = sol_model._read_group(
            domain, groupby=list(groupby), aggregates=["id:max"]
        )
        lines = sol_model.browse([group[-1] for group in groups])
        return {group[:-1]: line for group, line in zip(groups, lines, strict=True)}

    def _get_catalog_line_last_price(self, line):
        """Price of a previous sale ``line`` in the product UoM, the one the
        catalog adds lines in."""
        return line.product_uom._compute_price(line.price_unit, line.product_id.uom_id)

    def _get_catalog_last_prices(self, product_ids, use_delivery_address=False):
        """Return {product_id: last_price} from previous confirmed orders for
        this partner.
        """
        last_lines = self._get_catalog_last_sale_lines(
            product_ids, use_delivery_address=use_delivery_address
        )
        return {
            product.id: self._get_catalog_line_last_price(line)
            for (product,), line in last_lines.items()
        }

    def _set_catalog_last_price_data(self, data, last_price):
        """Show ``last_price`` on the catalog card ``data`` and on the cards of
        its order lines."""
        for card in [data, *data.get("lines", [])]:
            card["catalogShowLastPrice"] = True
            if last_price:
                card["lastPrice"] = last_price

    def _apply_catalog_last_price(self, line, last_price):
        """Set ``last_price`` on the ``line`` just added from the catalog."""
        if not last_price:
            return
        # Keep technical_price_unit (pricelist price) so that
        # _compute_price_unit recognises this as a manual override
        # and does not reset it on subsequent recomputations.
        line.write(
            {
                "price_unit": last_price,
                "technical_price_unit": line.technical_price_unit,
            }
        )

    def _get_product_catalog_order_line_info(
        self,
        product_ids,
        catalog_show_last_price=False,
        catalog_use_delivery_address=False,
        **kwargs,
    ):
        result = super()._get_product_catalog_order_line_info(product_ids, **kwargs)
        for product, lines in self._get_product_catalog_record_lines(
            list(result.keys()), **kwargs
        ).items():
            if len(lines) > 1:
                result[product.id]["lines"] = [
                    {
                        **line._get_product_catalog_lines_data(**kwargs),
                        "lineId": line.id,
                        "productType": product.type,
                    }
                    for line in lines
                ]
        for data in result.values():
            # Sent back by the catalog record on its own requests.
            data["catalogUseDeliveryAddress"] = catalog_use_delivery_address
        if not catalog_show_last_price:
            return result
        last_prices = self._get_catalog_last_prices(
            list(result.keys()), use_delivery_address=catalog_use_delivery_address
        )
        for product_id, data in result.items():
            self._set_catalog_last_price_data(data, last_prices.get(product_id, 0.0))
        return result

    def _get_catalog_line_quantity_vals(self, product, quantity, line=False):
        """Values that set ``quantity``, as typed in the catalog, on ``line`` or
        on a new line of ``product``. Hook for modules changing the unit the
        catalog quantity is expressed in (e.g. secondary units).
        """
        return {"product_uom_qty": quantity}

    def _get_catalog_line_onchange_fields(self):
        """Trigger fields whose ``@api.onchange`` methods must be replayed when
        a line is created from the catalog.
        """
        return ["product_id"]

    def _play_catalog_line_onchanges(self, line):
        """Replay on ``line`` the ``@api.onchange`` methods that adding a
        product from the catalog skips.
        """
        line.ensure_one()
        values = line.play_onchanges({}, self._get_catalog_line_onchange_fields())
        if values:
            line.write(values)

    def _update_order_line_info(
        self,
        product_id,
        quantity,
        catalog_show_last_price=False,
        catalog_use_delivery_address=False,
        **kwargs,
    ):
        is_new_line = quantity > 0 and not self.order_line.filtered(
            lambda line: line.product_id.id == product_id
        )
        result = super()._update_order_line_info(product_id, quantity, **kwargs)
        if not is_new_line:
            return result
        sol = self.order_line.filtered(lambda line: line.product_id.id == product_id)
        if not sol:
            return result
        # Replay the line onchanges that the base catalog ``create`` skips.
        self._play_catalog_line_onchanges(sol)
        result = sol._get_discounted_price()
        if catalog_show_last_price:
            last_price = self._get_catalog_last_prices(
                [product_id], use_delivery_address=catalog_use_delivery_address
            ).get(product_id, 0.0)
            self._apply_catalog_last_price(sol, last_price)
            result = sol._get_discounted_price()
        return result

    def _add_catalog_last_sales_exclusion(self, product_id, use_delivery_address=False):
        """Exclude ``product_id`` from the catalog *Last sales* option for the
        partner the catalog matches the sale history against.

        Creating the exclusion is idempotent: asking twice for the same partner
        and product keeps the existing record.
        """
        self.ensure_one()
        partner = self._catalog_history_partner(use_delivery_address)
        if not partner:
            return False
        exclusion_model = self.env["sale.catalog.product.exclusion"]
        exclusion = exclusion_model.search(
            [("partner_id", "=", partner.id), ("product_id", "=", product_id)],
            limit=1,
        )
        if not exclusion:
            exclusion = exclusion_model.create(
                {"partner_id": partner.id, "product_id": product_id}
            )
        return exclusion.id

    def _remove_catalog_last_sales_exclusions(self, products=None):
        """Drop the *Last sales* exclusions of the products sold in these orders.

        Selling a product to the partner again means it is relevant for them
        once more, so the exclusion is removed and the product goes back to the
        *Last sales* option. Both the commercial partner and the delivery
        address are cleaned up, as the history can be matched against either.

        :param products: products to clean up, defaulting to every product of
            the order lines. Adding a line to an already confirmed order passes
            only its products, as the ones already there were not sold again.
        """
        exclusion_model = self.env["sale.catalog.product.exclusion"].sudo()
        for order in self:
            partners = order._catalog_history_partner() | (
                order._catalog_history_partner(use_delivery_address=True)
            )
            sold = order.order_line.product_id if products is None else products
            if not partners or not sold:
                continue
            exclusion_model.search(
                [
                    ("partner_id", "in", partners.ids),
                    ("product_id", "in", sold.ids),
                ]
            ).unlink()

    def action_confirm(self):
        res = super().action_confirm()
        self._remove_catalog_last_sales_exclusions()
        return res

    @api.model
    def _get_catalog_order_line_filter_domain(self, product_id, **kwargs):
        """Get the domain used to filter lines from catalog."""
        return [("product_id", "=", product_id)]

    def _get_catalog_order_line(self, product_id, **kwargs):
        """Return the ids of the catalog order lines to be able to open
        them from catalog.
        """
        self.ensure_one()
        return self.order_line.filtered_domain(
            self._get_catalog_order_line_filter_domain(product_id, **kwargs)
        ).ids

    @api.model
    def _get_catalog_search_panel_fields(self):
        """Display-only ``product.product`` fields of the catalog search panel
        whose default value preselects them."""
        return [
            "catalog_origin_data",
            "catalog_last_sales",
            "catalog_price_mode",
            "catalog_history_partner",
        ]

    def _get_action_add_from_catalog_extra_context(self):
        context = {
            **super()._get_action_add_from_catalog_extra_context(),
            **self._get_catalog_history_context(),
        }
        # The search panel only takes its initial value from the context, so
        # forward the field defaults (ir.default, also set from the settings).
        defaults = self.env["product.product"].default_get(
            self._get_catalog_search_panel_fields()
        )
        for field_name, value in defaults.items():
            if value:
                context[f"searchpanel_default_{field_name}"] = value
        context["catalog_show_history_partner"] = bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_product_catalog_extended.catalog_show_history_partner")
        )
        return context
