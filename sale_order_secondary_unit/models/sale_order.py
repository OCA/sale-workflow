# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    secondary_uom_qty = fields.Float(
        string='Secondary Qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    secondary_uom_id = fields.Many2one(
        comodel_name='product.secondary.unit',
        string='Secondary uom',
        ondelete='restrict',
    )

    @api.onchange('secondary_uom_id', 'secondary_uom_qty')
    def onchange_secondary_uom(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_uom.rounding
        )
        if float_compare(
                self.product_uom_qty, qty,
                precision_rounding=self.product_uom.rounding) != 0:
            self.product_uom_qty = qty

    @api.onchange('product_uom_qty')
    def onchange_secondary_unit_product_uom_qty(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=self.secondary_uom_id.uom_id.rounding
        )
        if float_compare(
                self.secondary_uom_qty, qty,
                precision_rounding=self.secondary_uom_id.uom_id.rounding) != 0:
            self.secondary_uom_qty = qty

    @api.onchange('product_uom')
    def onchange_product_uom_for_secondary(self):
        if not self.secondary_uom_id:
            return
        factor = self.product_uom.factor * self.secondary_uom_id.factor
        qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=self.product_uom.rounding
        )
        if float_compare(
                self.secondary_uom_qty, qty,
                precision_rounding=self.product_uom.rounding) != 0:
            self.secondary_uom_qty = qty

    @api.onchange('product_id')
    def product_id_change(self):
        """
        If default sales secondary unit set on product, put on secondary
        quantity 1 for being the default quantity. We override this method,
        that is the one that sets by default 1 on the other quantity with that
        purpose.
        """
        res = super(SaleOrderLine, self).product_id_change()
        self.secondary_uom_id = self.product_id.sale_secondary_uom_id
        if self.secondary_uom_id:
            self.secondary_uom_qty = 1.0
            self.onchange_secondary_uom()
        return res
