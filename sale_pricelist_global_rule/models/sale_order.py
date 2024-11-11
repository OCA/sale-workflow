from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    need_recompute_pricelist_global = fields.Boolean()
    has_pricelist_global = fields.Boolean(compute="_compute_has_pricelist_global")

    @api.depends("pricelist_id")
    def _compute_has_pricelist_global(self):
        for sale in self:
            if not sale.pricelist_id:
                sale.has_pricelist_global = False
                continue
            (
                prod_tmpl_ids,
                categ_ids,
            ) = sale.pricelist_id._extract_products_and_categs_from_sale(sale)
            items = sale.pricelist_id._compute_price_rule_get_items_globals(
                sale.date_order, prod_tmpl_ids, categ_ids
            )
            sale.has_pricelist_global = bool(items)

    @api.onchange("order_line")
    def _onchange_need_recompute_pricelist_global(self):
        self.need_recompute_pricelist_global = True

    def button_compute_pricelist_global_rule(self):
        self.ensure_one()
        prices_data = self.pricelist_id._compute_price_rule_global(self)
        digits = self.pricelist_id.currency_id.decimal_places
        is_discount_visible = (
            self.pricelist_id.discount_policy == "without_discount"
            and self.env.user.has_group("product.group_discount_per_so_line")
        )
        for line in self.order_line.filtered(lambda x: not x.display_type):
            vals_to_write = {"discount": 0.0}
            product = line.product_id.with_context(
                lang=self.partner_id.lang,
                partner=self.partner_id,
                quantity=line.product_uom_qty,
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=line.product_uom.id,
                fiscal_position=self.env.context.get("fiscal_position"),
            )
            price, suitable_rule = prices_data[line.id]
            if is_discount_visible:
                product_context = dict(
                    self.env.context,
                    partner_id=self.partner_id.id,
                    date=self.date_order,
                    uom=line.product_uom.id,
                )

                base_price, currency = line.with_context(
                    **product_context
                )._get_real_price_currency(
                    product,
                    suitable_rule,
                    line.product_uom_qty,
                    line.product_uom,
                    self.pricelist_id.id,
                )
                if base_price != 0:
                    if self.pricelist_id.currency_id != currency:
                        # we need new_list_price in the same currency as price,
                        # which is in the SO's pricelist's currency
                        base_price = currency._convert(
                            base_price,
                            self.pricelist_id.currency_id,
                            self.company_id or self.env.company,
                            self.date_order or fields.Date.context_today(self),
                        )
                    discount = (base_price - price) / base_price * 100
                    if (discount > 0 and base_price > 0) or (
                        discount < 0 and base_price < 0
                    ):
                        vals_to_write["discount"] = discount
                price = max(base_price, price)

            if float_compare(price, line.price_unit, precision_digits=digits) != 0:
                vals_to_write["price_unit"] = price
            if vals_to_write:
                line.write(vals_to_write)
        self.need_recompute_pricelist_global = False
