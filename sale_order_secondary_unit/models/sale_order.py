# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }


    def _get_factor_line(self):
        res = 1.0
        if not self.secondary_uom_id and self.product_id.secondary_uom_ids:
            res = self.product_id.secondary_uom_ids.uom_id.factor or 1.0
        res = super()._get_factor_line()
        return res

    @api.onchange("secondary_uom_id", "secondary_uom_qty")
    def onchange_secondary_uom(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("product_uom_qty")
    def onchange_secondary_unit_product_uom_qty(self):
        if not self.secondary_uom_id:
            self.product_uom_qty = self.product_uom_qty or 1.0
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=self.secondary_uom_id.uom_id.rounding,
        )

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("product_id")
    def product_id_change(self):
        """
        If default sales secondary unit set on product, put on secondary
        quantity 1 for being the default quantity. We override this method,
        that is the one that sets by default 1 on the other quantity with that
        purpose.
        """
        res = super().product_id_change()
        self.secondary_uom_id = self.product_id.product_tmpl_id._get_default_secondary_uom()
        if self.secondary_uom_id:
            self.secondary_uom_qty = 1.0
            self.onchange_secondary_uom()
        return res
