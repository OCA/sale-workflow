# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_min_qty = fields.Float(
        string="Min Qty",
        related="product_id.sale_min_qty",
        readonly=True,
        store=True,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    force_sale_min_qty = fields.Boolean(
        related="product_id.force_sale_min_qty", readonly=True, store=True
    )
    is_qty_less_min_qty = fields.Boolean(
        string="Qty < Min Qty", compute="_compute_is_qty_less_min_qty"
    )

    @api.constrains("product_uom_qty")
    def check_constraint_min_qty(self):
        for line in self:
            invaild_lines = []
            rounding = line.product_uom.rounding
            line_to_test = line.filtered(
                lambda l: not l.product_id.force_sale_min_qty
                and float_compare(
                    l.product_uom_qty,
                    l.product_id.sale_min_qty,
                    precision_rounding=rounding,
                )
                < 0
            )
            for line in line_to_test:
                invaild_lines.append(
                    _('Product "%s": Min Quantity %s.')
                    % (line.product_id.name, line.product_id.sale_min_qty)
                )

            if invaild_lines:
                msg = _(
                    "Check minimum order quantity for this products: * \n"
                ) + "\n ".join(invaild_lines)
                msg += _(
                    "\n* If you want sell quantity less than Min Quantity"
                    ',Check "force min quatity" on product'
                )
                raise ValidationError(msg)

    @api.multi
    @api.depends("product_uom_qty", "sale_min_qty")
    def _compute_is_qty_less_min_qty(self):
        for line in self:
            rounding = self.product_uom.rounding
            line.is_qty_less_min_qty = (
                float_compare(
                    line.product_uom_qty,
                    line.sale_min_qty,
                    precision_rounding=rounding,
                )
                < 0
            )
