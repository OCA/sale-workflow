from functools import partial

from odoo import models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(
                formatLang,
                self.with_context(lang=order.partner_id.lang).env,
                currency_obj=currency,
            )
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(
                    price_reduce,
                    quantity=line.product_uom_qty,
                    product=line.product_id,
                    partner=order.partner_shipping_id,
                )["taxes"]
                for tax in line.tax_id:
                    tax_name = tax.name or tax.tax_group_id.name
                    res.setdefault(
                        tax_name, {"amount": 0.0, "base": 0.0, "sequence": tax.sequence}
                    )
                    for t in taxes:
                        if t["id"] == tax.id or t["id"] in tax.children_tax_ids.ids:
                            res[tax_name]["amount"] += t["amount"]
                            res[tax_name]["base"] += t["base"]
            res = sorted(res.items(), key=lambda l: l[1]["sequence"])
            for _tax_name, values in res:
                values["amount"] = currency.round(values["amount"]) + 0.0
                values["base"] = currency.round(values["base"]) + 0.0
            order.amount_by_group = [
                (
                    tax_name,
                    values["amount"],
                    values["base"],
                    fmt(values["amount"]),
                    fmt(values["base"]),
                    len(res),
                )
                for tax_name, values in res
            ]
