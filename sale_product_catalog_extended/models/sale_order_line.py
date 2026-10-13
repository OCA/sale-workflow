# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools.misc import clean_context

# Card parameters (see ``_getUpdateQuantityAndGetPriceParams`` in the catalog
# kanban record) that are not catalog options of the line.
CATALOG_CARD_PARAMS = ("order_id", "product_id", "quantity", "res_model", "child_field")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_catalog_form_card(self):
        """Return ``(order, product, card options)`` of the catalog card that
        opened the new line form, from the ``catalog_line_params`` context key,
        or empty records and ``{}`` when the line does not come from a card.
        """
        params = self.env.context.get("catalog_line_params")
        order = self.env["sale.order"]
        product = self.env["product.product"]
        if not isinstance(params, dict) or not params.get("product_id"):
            return order, product, {}
        options = {
            key: value
            for key, value in params.items()
            if key not in CATALOG_CARD_PARAMS
        }
        return (
            order.browse(params.get("order_id")),
            product.browse(params["product_id"]),
            options,
        )

    @api.model
    def default_get(self, fields_list):
        """Start the line opened from a catalog card with the values the
        catalog sets on the lines it adds (see
        ``sale.order._get_catalog_new_line_vals``).
        """
        defaults = super().default_get(fields_list)
        order, product, options = self._get_catalog_form_card()
        # ``create`` only asks for the defaults of the fields it misses, so the
        # order and the product are taken from the card.
        if (
            not order
            or defaults.get("order_id", order.id) != order.id
            or defaults.get("product_id", product.id) != product.id
        ):
            return defaults
        vals = {
            **order._get_catalog_new_line_vals(product, **options),
            # The quantity the card Add button puts, in the unit of the card.
            **order._get_catalog_line_quantity_vals(product, 1.0),
        }
        defaults.update(
            {name: value for name, value in vals.items() if name in fields_list}
        )
        return defaults

    def _compute_price_unit(self):
        """Price the line opened from a catalog card showing the last sale
        prices with that last price, as the catalog does on the lines it adds
        (see ``sale.order._apply_catalog_last_price``).
        """
        res = super()._compute_price_unit()
        __, product, options = self._get_catalog_form_card()
        if not product or not options.get("catalog_show_last_price"):
            return res
        for line in self:
            # Only the new line of the card product, before it is saved: once
            # in the database the line is handled as any other one.
            if line._origin or line.product_id != product or not line.order_id:
                continue
            currency = line.currency_id or line.order_id.currency_id
            # A manual price, including the last price already applied, is kept.
            if currency.compare_amounts(line.technical_price_unit, line.price_unit):
                continue
            last_price = line.order_id._get_catalog_new_line_last_price(
                product.id, **options
            )
            if last_price:
                # technical_price_unit keeps the pricelist price, so the core
                # compute takes it as a manual price from now on.
                line.price_unit = last_price
        return res

    def _remove_catalog_last_sales_exclusions(self):
        """Drop the *Last sales* exclusions of these lines' products when their
        order is already confirmed, which the clean up done on confirmation
        cannot cover.

        Only the products of these lines are cleaned up: the ones already in the
        order were not sold again by this change.
        """
        for order, lines in self.grouped("order_id").items():
            if order.state != "sale":
                continue
            order._remove_catalog_last_sales_exclusions(products=lines.product_id)

    @api.model_create_multi
    def create(self, vals_list):
        if "catalog_line_params" in self.env.context:
            # The form opened from a catalog card does not send its readonly
            # fields (e.g. the vendor of a confirmed order), so their defaults
            # (see ``default_get``) are added while the context still has them.
            # Then its ``default_*`` keys must not reach the records created
            # along with the line (e.g. the stock moves of a confirmed order).
            vals_list = [self._add_missing_default_values(vals) for vals in vals_list]
            context = clean_context(self.env.context)
            context.pop("catalog_line_params")
            self = self.with_env(self.env(context=context))  # pylint: disable=self-cls-assignment
        lines = super().create(vals_list)
        lines._remove_catalog_last_sales_exclusions()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if "product_id" in vals:
            self._remove_catalog_last_sales_exclusions()
        return res
