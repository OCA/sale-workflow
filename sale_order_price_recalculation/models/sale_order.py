# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _recompute_form_line_vals(self, fields):
        """Helper method for writing in line certain recomputed by onchanges fields."""
        for line in self.mapped("order_line"):
            vals = line._convert_to_write(line.read()[0])
            if "product_tmpl_id" in line._fields:
                vals["product_tmpl_id"] = line.product_tmpl_id
            # we make this to isolate changed values:
            line2 = self.env["sale.order.line"].new(vals)
            line2.env.add_to_compute(
                line2.product_id._fields["price"], line2.product_id
            )
            line2.product_id_change()
            line2._onchange_discount()
            line.write({field: line2[field] for field in fields})

    def recalculate_prices(self):
        self._recompute_form_line_vals(["price_unit", "discount"])
        return True

    def recalculate_names(self):
        self._recompute_form_line_vals(["name"])
        return True
