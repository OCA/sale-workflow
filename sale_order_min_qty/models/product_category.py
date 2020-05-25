# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductCategory(models.Model):
    _inherit = "product.category"

    sale_multiple_qty = fields.Float(
        compute="_compute_sale_multiple_qty",
        store=True,
        help="Define sale multiple qty"
        " 'If not set', Odoo will"
        " use the value defined in the parent category.",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    manual_sale_multiple_qty = fields.Float(
        string="multiple Sale Qty", digits=dp.get_precision("Product Unit of Measure")
    )
    sale_min_qty = fields.Float(
        compute="_compute_sale_min_qty",
        store=True,
        help="Define sale min qty"
        " 'If not set, Odoo will"
        " use the value defined in the parent category.",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    manual_sale_min_qty = fields.Float(
        string="Min Sale Qty", digits=dp.get_precision("Product Unit of Measure")
    )
    force_sale_min_qty = fields.Float(
        compute="_compute_force_sale_min_qty",
        string="Force Min Qty",
        store=True,
        help="Define if user can force sale min qty"
        " 'If not set', Odoo will"
        " use the value defined in the parent category.",
    )
    manual_force_sale_min_qty = fields.Boolean(
        string="Manual Force Min Qty",
        help="If force min qty is checked, the min quantity "
        "is only indicative value.",
    )

    @api.depends("parent_id.force_sale_min_qty", "manual_force_sale_min_qty")
    def _compute_force_sale_min_qty(self):
        for rec in self:
            rec.sale_min_qty = (
                rec.manual_force_sale_min_qty or rec.parent_id.force_sale_min_qty
            )

    @api.depends("parent_id.sale_min_qty", "manual_sale_min_qty")
    def _compute_sale_min_qty(self):
        for rec in self:
            rec.sale_min_qty = rec.manual_sale_min_qty or rec.parent_id.sale_min_qty

    @api.depends("parent_id.sale_multiple_qty", "manual_sale_multiple_qty")
    def _compute_sale_multiple_qty(self):
        for rec in self:
            rec.sale_multiple_qty = (
                rec.manual_sale_multiple_qty or rec.parent_id.sale_multiple_qty
            )
