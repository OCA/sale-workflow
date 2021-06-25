# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
<<<<<<< HEAD
<<<<<<< HEAD
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
=======
from odoo.tools.float_utils import float_compare, float_round
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
||||||| parent of d16be0e27 ([FIX] code refactor)
from odoo.tools.float_utils import float_compare, float_round
=======
from odoo.tools.float_utils import float_round
>>>>>>> d16be0e27 ([FIX] code refactor)


class SaleOrderLine(models.Model):
<<<<<<< HEAD
<<<<<<< HEAD
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
    _inherit = 'sale.order.line'
=======
    _inherit = "sale.order.line"
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
||||||| parent of d16be0e27 ([FIX] code refactor)
    _inherit = "sale.order.line"
=======
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }
>>>>>>> d16be0e27 ([FIX] code refactor)

<<<<<<< HEAD
<<<<<<< HEAD
    secondary_uom_unit_price = fields.Float(
        string="2nd unit price",
        digits="Product Price",
        compute="_compute_secondary_uom_unit_price",
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
    secondary_uom_qty = fields.Float(
        string='Secondary Qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    secondary_uom_id = fields.Many2one(
        comodel_name='product.secondary.unit',
        string='Secondary uom',
        ondelete='restrict',
=======
    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Secondary uom",
        ondelete="restrict",
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
    )
||||||| parent of d16be0e27 ([FIX] code refactor)
    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Secondary uom",
        ondelete="restrict",
    )
=======

    def _get_factor_line(self):
        res = 1.0
        if not self.secondary_uom_id and self.product_id.secondary_uom_ids:
            res = self.product_id.secondary_uom_ids.uom_id.factor or 1.0
        res = super()._get_factor_line()
        return res
>>>>>>> d16be0e27 ([FIX] code refactor)

<<<<<<< HEAD
    product_uom_qty = fields.Float(copy=True)
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
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
=======
    @api.onchange("secondary_uom_id", "secondary_uom_qty")
    def onchange_secondary_uom(self):
<<<<<<< HEAD
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.product_uom_qty, qty, precision_rounding=self.product_uom.rounding
            )
            != 0
        ):
            self.product_uom_qty = qty
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
||||||| parent of d16be0e27 ([FIX] code refactor)
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.product_uom_qty, qty, precision_rounding=self.product_uom.rounding
            )
            != 0
        ):
            self.product_uom_qty = qty
=======
        self._onchange_helper_product_uom_for_secondary()
>>>>>>> d16be0e27 ([FIX] code refactor)

<<<<<<< HEAD
    @api.depends(
        "display_type",
        "product_id",
        "product_packaging_qty",
        "secondary_uom_qty",
        "secondary_uom_id",
        "product_uom_qty",
    )
    def _compute_product_uom_qty(self):
        res = super()._compute_product_uom_qty()
        for line in self:
            line._compute_helper_target_field_qty()
        return res
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
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
=======
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
<<<<<<< HEAD
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.secondary_uom_id.uom_id.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
||||||| parent of d16be0e27 ([FIX] code refactor)
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.secondary_uom_id.uom_id.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty
=======
>>>>>>> d16be0e27 ([FIX] code refactor)

<<<<<<< HEAD
    @api.depends("product_id")
    def _compute_product_uom(self):
        res = super()._compute_product_uom()
        for line in self:
            line._onchange_helper_product_uom_for_secondary()
        return res
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
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
=======
    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
<<<<<<< HEAD
        if not self.secondary_uom_id:
            return
        factor = self.product_uom.factor * self.secondary_uom_id.factor
        qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.product_uom.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
||||||| parent of d16be0e27 ([FIX] code refactor)
        if not self.secondary_uom_id:
            return
        factor = self.product_uom.factor * self.secondary_uom_id.factor
        qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.product_uom.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty
=======
        self._onchange_helper_product_uom_for_secondary()
>>>>>>> d16be0e27 ([FIX] code refactor)

<<<<<<< HEAD
<<<<<<< HEAD
    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()
        if self.product_id and not self.env.context.get("skip_secondary_uom_default"):
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.product_uom_qty == 1.0:
                self.secondary_uom_qty = 1.0
                self._onchange_helper_product_uom_for_secondary()
        return res

    @api.depends("secondary_uom_qty", "product_uom_qty", "price_unit")
    def _compute_secondary_uom_unit_price(self):
        for line in self:
            if line.secondary_uom_id:
                try:
                    line.secondary_uom_unit_price = (
                        line.price_subtotal / line.secondary_uom_qty
                    )
                except ZeroDivisionError:
                    line.secondary_uom_unit_price = 0
            else:
                line.secondary_uom_unit_price = 0
||||||| parent of 90d059d1c ([11.0][IMP] sale_secondary_unit: Set secondary uom quantity as 1.0 by default)
    @api.onchange('product_id')
    def onchange_secondary_unit_product_id(self):
        self.secondary_uom_id = self.product_id.sale_secondary_uom_id
=======
    @api.onchange('product_id')
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
    @api.onchange('product_id')
=======
    @api.onchange("product_id")
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
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
>>>>>>> 90d059d1c ([11.0][IMP] sale_secondary_unit: Set secondary uom quantity as 1.0 by default)
