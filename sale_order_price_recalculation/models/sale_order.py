# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def recalculate_prices(self):
        for line in self.mapped("order_line"):
            dict = line._convert_to_write(line.read()[0])
            if "product_tmpl_id" in line._fields:
                dict["product_tmpl_id"] = line.product_tmpl_id
            line2 = self.env["sale.order.line"].new(dict)
            # we make this to isolate changed values:
            line2.product_uom_change()
            line2._onchange_discount()
            line.write(
                {"price_unit": line2.price_unit, "discount": line2.discount,}
            )
        return True

    @api.multi
    def recalculate_names(self):
        for line in self.mapped("order_line").filtered("product_id"):
            # we make this to isolate changed values:
            line2 = self.env["sale.order.line"].new({"product_id": line.product_id,})
            line2.product_id_change()
            line.name = line2.name
        return True
