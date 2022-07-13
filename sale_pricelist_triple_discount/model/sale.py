# Copyright 2019 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(
        self,
        pricelist,
        product,
        qty=0,
        uom=False,
        qty_uos=0,
        uos=False,
        name="",
        partner_id=False,
        lang=False,
        update_tax=True,
        date_order=False,
        packaging=False,
        fiscal_position=False,
        flag=False,
    ):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist,
            product,
            qty=qty,
            uom=uom,
            qty_uos=qty_uos,
            uos=uos,
            name=name,
            partner_id=partner_id,
            lang=lang,
            update_tax=update_tax,
            date_order=date_order,
            packaging=packaging,
            fiscal_position=fiscal_position,
            flag=flag,
        )
        if product and pricelist:
            value = res["value"]
            current_pricelist = self.env["product.pricelist"].browse(pricelist)
            list_price = current_pricelist.price_rule_get(
                product, qty or 1.0, partner_id
            )
            rule_id = list_price.get(pricelist) and list_price[pricelist][1] or False
            rule = self.env["product.pricelist.item"].browse(rule_id)
            read_rule = rule.read(["discount2", "discount3"])[0]
            value["discount2"] = read_rule["discount2"] or 0.00
            value["discount3"] = read_rule["discount3"] or 0.00
        return res
