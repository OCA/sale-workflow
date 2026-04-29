from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    _PRICE_SOURCE_SYNC_FIELDS = {
        "product_id",
        "product_uom_id",
        "product_uom_qty",
        "price_unit",
        "technical_price_unit",
    }

    price_source = fields.Selection(
        [
            ("pricelist", "Pricelist Rule"),
            ("product", "Product Sales Price"),
            ("manual", "Manual Override"),
        ],
        default="product",
        help="Indicates the source of the unit price: Pricelist rule, "
        "product base price, or manual override.",
    )

    price_source_pricelist_item_id = fields.Many2one(
        "product.pricelist.item",
        help="The pricelist rule that determined "
        "this line's price (if source is Pricelist).",
    )

    def _has_manual_price(self):
        """
        Mirror core manual-price detection from
        sale.order.line._compute_price_unit.
        """
        self.ensure_one()
        currency = (
            self.currency_id
            or self.company_id.currency_id
            or self.env.company.currency_id
        )
        return bool(
            currency.compare_amounts(self.technical_price_unit, self.price_unit)
        )

    def _sync_price_source_from_pricing(self):
        """
        Sync provenance from the same pricing state that core sale.order.line uses.
        """
        for line in self.filtered(
            lambda record: not record.display_type and record.product_id
        ):
            values = {
                "price_source": "product",
                "price_source_pricelist_item_id": False,
            }

            if line._has_manual_price():
                values["price_source"] = "manual"
            else:
                line._compute_pricelist_item_id()
                if line.pricelist_item_id:
                    values = {
                        "price_source": "pricelist",
                        "price_source_pricelist_item_id": line.pricelist_item_id.id,
                    }

            if (
                line.price_source != values["price_source"]
                or line.price_source_pricelist_item_id.id
                != values["price_source_pricelist_item_id"]
            ):
                super(
                    SaleOrderLine, line.with_context(skip_price_source_update=True)
                ).write(values)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._sync_price_source_from_pricing()
        return lines

    def write(self, values):
        should_sync = bool(self._PRICE_SOURCE_SYNC_FIELDS.intersection(values))
        result = super().write(values)

        if should_sync and not self.env.context.get("skip_price_source_update"):
            self._sync_price_source_from_pricing()

        return result

    def _reset_price_unit(self):
        result = super(
            SaleOrderLine, self.with_context(skip_price_source_update=True)
        )._reset_price_unit()
        self._sync_price_source_from_pricing()
        return result
