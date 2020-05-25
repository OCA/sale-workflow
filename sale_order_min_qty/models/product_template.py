# Copyright 2019 Akretion
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_multiple_qty_tmpl = fields.Float(
        compute="_compute_sale_multiple_qty_tmpl",
        store=True,
        help="Define sale multiple qty"
        " 'If not set', Odoo will"
        " use the value defined in the product category.",
        digits=dp.get_precision("Stock Threshold"),
    )
    manual_sale_multiple_qty_tmpl = fields.Float(
        string="multiple Sale Qty",
        digits=dp.get_precision("Product Unit of Measure")
    )
    sale_min_qty_tmpl = fields.Float(
        compute="_compute_sale_min_qty_tmpl",
        store=True,
        help="Define sale min qty"
        " 'If not set', Odoo will"
        " use the value defined in the product category.",
        digits=dp.get_precision("Stock Threshold"),
    )
    manual_sale_min_qty_tmpl = fields.Float(
        string="Min Se Qty", digits=dp.get_precision("Product Unit of Measure")
    )
    force_sale_min_qty_tmpl = fields.Boolean(
        compute="_compute_force_sale_min_qty_tmpl",
        string="Force Min Qty",
        store=True,
        help="Define if user can force sale min qty"
        " 'If not set, Odoo will"
        " use the value defined in the product category.",
    )
    manual_force_sale_min_qty_tmpl = fields.Boolean(
        string="Manual Force Min Qty",
        help="If force min qty is checked, the min quantity "
        "is only indicative value.",
    )

    @api.depends("categ_id.force_sale_min_qty",
                 "manual_force_sale_min_qty_tmpl")
    def _compute_force_sale_min_qty_tmpl(self):
        for rec in self:
            rec.sale_min_qty_tmpl = (
                rec.manual_force_sale_min_qty_tmpl or
                rec.categ_id.force_sale_min_qty
            )

    @api.depends("categ_id.sale_min_qty", "manual_sale_min_qty_tmpl")
    def _compute_sale_min_qty_tmpl(self):
        for rec in self:
            rec.sale_min_qty_tmpl = (
                rec.manual_sale_min_qty_tmpl or rec.categ_id.sale_min_qty
            )

    @api.depends("categ_id.sale_multiple_qty", "manual_sale_multiple_qty_tmpl")
    def _compute_sale_multiple_qty_tmpl(self):
        for rec in self:
            rec.sale_multiple_qty_tmpl = (
                rec.manual_sale_multiple_qty_tmpl or
                rec.categ_id.sale_multiple_qty
            )
