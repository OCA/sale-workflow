# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright (c) 2021 Andrea Cometa - Apulia Software s.r.l.
# Copyright 2022 Alberto Re - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from functools import partial

from odoo import api, models, tools
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _amount_by_group(self):
        super()._amount_by_group()

        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(
                formatLang,
                self.with_context(lang=order.partner_id.lang).env,
                currency_obj=currency,
            )
            res = {}

            for line in order.order_line:
                current_pricelist = self.pricelist_id
                if not (
                    line.product_id
                    and line.product_uom
                    and self.partner_id
                    and current_pricelist
                    and self.env.user.has_group("product.group_discount_per_so_line")
                ):
                    continue

                list_price = current_pricelist.price_rule_get(
                    line.product_id.id,
                    line.product_uom_qty or 1.0,
                    line.order_id.partner_id.id,
                )
                rule_id = (
                    list_price.get(current_pricelist.id)
                    and list_price[current_pricelist.id][1]
                    or False
                )
                rule = self.env["product.pricelist.item"].browse(rule_id)

                if not rule.price_round:
                    continue

                rounded_price_subtotal = tools.float_round(
                    line.price_subtotal, precision_rounding=rule.price_round
                )
                taxes = line.tax_id.compute_all(
                    rounded_price_subtotal,
                    line.order_id.currency_id,
                    1,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )["taxes"]

                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {"amount": 0.0, "base": 0.0})
                    for t in taxes:
                        if t["id"] == tax.id or t["id"] in tax.children_tax_ids.ids:
                            res[group]["amount"] += t["amount"]
                            res[group]["base"] += t["base"]
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [
                (
                    entry[0].name,
                    entry[1]["amount"],
                    entry[1]["base"],
                    fmt(entry[1]["amount"]),
                    fmt(entry[1]["base"]),
                    len(res),
                )
                for entry in res
            ]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange(
        "product_id", "price_unit", "product_uom", "product_uom_qty", "tax_id"
    )
    def _onchange_discount(self):
        super()._onchange_discount()

        pricelist = self.order_id.pricelist_id
        if not (
            self.product_id
            and self.product_uom
            and self.order_id.partner_id
            and pricelist
            and pricelist.discount_policy == "without_discount"
            and self.env.user.has_group("product.group_discount_per_so_line")
        ):
            return

        current_pricelist = self.order_id.pricelist_id
        list_price = current_pricelist.price_rule_get(
            self.product_id.id, self.product_uom_qty or 1.0, self.order_id.partner_id.id
        )
        rule_id = (
            list_price.get(current_pricelist.id)
            and list_price[current_pricelist.id][1]
            or False
        )
        if rule_id:
            rule = self.env["product.pricelist.item"].browse(rule_id)
            read_rule = rule.read(["discount2", "discount3"])[0]
            self.discount2 = read_rule["discount2"] or 0.00
            self.discount3 = read_rule["discount3"] or 0.00

    @api.depends(
        "product_uom_qty",
        "discount",
        "price_unit",
        "tax_id",
        "discount2",
        "discount3",
        "discounting_type",
    )
    def _compute_amount(self):
        super()._compute_amount()

        current_pricelist = self.order_id.pricelist_id
        if not (
            self.product_id
            and self.product_uom
            and self.order_id.partner_id
            and current_pricelist
            and self.env.user.has_group("product.group_discount_per_so_line")
        ):
            return

        for line in self:

            list_price = current_pricelist.price_rule_get(
                line.product_id.id,
                line.product_uom_qty or 1.0,
                line.order_id.partner_id.id,
            )
            rule_id = (
                list_price.get(current_pricelist.id)
                and list_price[current_pricelist.id][1]
                or False
            )
            rule = self.env["product.pricelist.item"].browse(rule_id)

            if not rule.price_round:
                return

            rounded_price_subtotal = tools.float_round(
                line.price_subtotal, precision_rounding=rule.price_round
            )

            if current_pricelist.discount_policy == "without_discount":
                read_rule = rule.read(["price_discount"])[0]
                if line.discount2:
                    line.discount = read_rule["price_discount"]
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    price = price * line.product_uom_qty
                    if line.discount3:
                        price = (price - (price * (line.discount2 / 100))) or 0.0
                        line.discount3 = 100 - (rounded_price_subtotal / price * 100)
                    else:
                        line.discount2 = 100 - (rounded_price_subtotal / price * 100)

            taxes = line.tax_id.compute_all(
                rounded_price_subtotal,
                line.order_id.currency_id,
                1,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line.update(
                {
                    "price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )

            line.update({"price_subtotal": rounded_price_subtotal})
