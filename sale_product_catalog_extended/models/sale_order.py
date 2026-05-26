# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_catalog_last_prices(self, product_ids):
        """Return {product_id: last_price} from previous confirmed orders for
        this partner.
        """
        if not product_ids:
            return {}
        domain = (
            self.env["product.product"]
            .with_context(
                product_catalog_partner_id=self.partner_shipping_id.id,
                product_catalog_order_id=self.id,
            )
            ._product_picker_data_sale_order_domain()
        )
        domain += [("product_id", "in", product_ids)]
        sol_groups = self.env["sale.order.line"]._read_group(
            domain,
            groupby=["product_id"],
            aggregates=["id:max"],
        )
        last_line_ids = [max_id for _product, max_id in sol_groups]
        if not last_line_ids:
            return {}
        lines = self.env["sale.order.line"].browse(last_line_ids)
        return {line.product_id.id: line.price_unit for line in lines}

    def _get_product_catalog_order_line_info(
        self, product_ids, catalog_show_last_price=False, **kwargs
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
        if not catalog_show_last_price:
            return result
        last_prices = self._get_catalog_last_prices(list(result.keys()))
        for product_id, data in result.items():
            data["catalogShowLastPrice"] = True
            last_price = last_prices.get(product_id, 0.0)
            if last_price:
                data["lastPrice"] = last_price
            for line_data in data.get("lines", []):
                line_data["catalogShowLastPrice"] = True
                if last_price:
                    line_data["lastPrice"] = last_price
        return result

    def _update_order_line_info(
        self, product_id, quantity, catalog_show_last_price=False, **kwargs
    ):
        is_new_line = (
            quantity > 0
            and catalog_show_last_price
            and not self.order_line.filtered(
                lambda line: line.product_id.id == product_id
            )
        )
        result = super()._update_order_line_info(product_id, quantity, **kwargs)
        if is_new_line:
            last_price = self._get_catalog_last_prices([product_id]).get(
                product_id, 0.0
            )
            if last_price:
                sol = self.order_line.filtered(
                    lambda line: line.product_id.id == product_id
                )
                if sol:
                    # Keep technical_price_unit (pricelist price) so that
                    # _compute_price_unit recognises this as a manual override
                    # and does not reset it on subsequent recomputations.
                    sol.write(
                        {
                            "price_unit": last_price,
                            "technical_price_unit": sol.technical_price_unit,
                        }
                    )
                    result = sol._get_discounted_price()
        return result

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

    def _get_action_add_from_catalog_extra_context(self):
        # TODO: partner_id or shipping_partner_id?
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            "product_catalog_partner_id": self.partner_shipping_id.id,
        }
