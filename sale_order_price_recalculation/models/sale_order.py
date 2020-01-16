# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def recalculate_prices(self):
        for line in self.mapped("order_line"):
            vals = line._convert_to_write(line.read()[0])
            if "product_tmpl_id" in line._fields:
                vals["product_tmpl_id"] = line.product_tmpl_id
            line2 = self.env["sale.order.line"].new(vals)
            # we make this to isolate changed values
            price_unit = self.env["account.tax"]._fix_tax_included_price_company(
                line2._get_display_price(line2.product_id),
                line2.product_id.taxes_id,
                line2.tax_id,
                line2.company_id,
            )
            line2._onchange_discount()
            line.write({"price_unit": price_unit, "discount": line2.discount})
        return True

    def recalculate_names(self):
        for line in self.mapped("order_line").filtered("product_id"):
            # we make this to isolate changed values:
            line2 = self.env["sale.order.line"].new({"product_id": line.product_id})
            line2.product_id_change()
            line.name = line2.name
        return True
