# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from functools import partial

from odoo import api, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.price_total")
    def _amount_all(self):
        prev_values = dict()
        for order in self:
            prev_values.update(order.order_line.triple_discount_preprocess())
        super()._amount_all()
        self.env["sale.order.line"].triple_discount_postprocess(prev_values)

    def _amount_by_group(self):
        # Copy/paste from standard method in sale
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(
                formatLang,
                self.with_context(lang=order.partner_id.lang).env,
                currency_obj=currency,
            )
            res = {}
            for line in order.order_line:
                price_reduce = line.price_reduce  # changed
                taxes = line.tax_id.compute_all(
                    price_reduce,
                    quantity=line.product_uom_qty,
                    product=line.product_id,
                    partner=order.partner_shipping_id,
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
                    l[0].name,
                    l[1]["amount"],
                    l[1]["base"],
                    fmt(l[1]["amount"]),
                    fmt(l[1]["base"]),
                    len(res),
                )
                for l in res
            ]
