# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models
from odoo.tests import Form


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _recompute_form_line_vals(self, fields):
        """Helper method for writing in line certain recomputed by onchanges fields."""
        self.ensure_one()
        so_form = Form(self)
        for index, line in enumerate(self.order_line):
            line_form = so_form.order_line.edit(index)
            line_form._perform_onchange(["product_id"])
            line_form._perform_onchange(["product_uom_qty"])
            vals = line_form._values_to_save(all_fields=True)
            line.write({field: vals[field] for field in fields})

    def recalculate_prices(self):
        for order in self:
            order._recompute_form_line_vals(["price_unit", "discount"])
        return True

    def recalculate_names(self):
        for order in self:
            order._recompute_form_line_vals(["name"])
        return True
