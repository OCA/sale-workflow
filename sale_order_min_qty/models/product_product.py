# Copyright 2019 Akretion
#  @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_multiple_qty = fields.Float(
        compute="_compute_sale_multiple_qty",
        store=True,
        help="Define sale multiple qty"
        " 'If not set, Odoo will"
        " use the value defined in the product template."
        " 'If not set', Odoo will"
        " use the value defined in the product category.",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    manual_sale_multiple_qty = fields.Float(
        string="multiple Sale Qty", digits=dp.get_precision("Product Unit of Measure")
    )
    sale_min_qty = fields.Float(
        compute="_compute_sale_min_qty",
        store=True,
        help="Define sale min qty"
        " 'If not set', Odoo will"
        " use the value defined in the product template."
        " 'If not set', Odoo will"
        " use the value defined in the product category.",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    manual_sale_min_qty = fields.Float(
        string="Min Sale Qty", digits=dp.get_precision("Product Unit of Measure")
    )
    force_sale_min_qty = fields.Boolean(
        compute="_compute_force_sale_min_qty",
        string="Force Min Qty",
        store=True,
        help="Define if user can force sale min qty"
        " 'If not set, Odoo will"
        " use the value defined in the product template."
        " 'If not set', Odoo will"
        " use the value defined in the product category.",
    )
    manual_force_sale_min_qty = fields.Boolean(
        string="Manual Force Min Qty",
        help="If force min qty is checked, the min quantity "
        "is only indicative value.",
    )

    @api.depends("force_sale_min_qty_tmpl", "manual_force_sale_min_qty")
    def _compute_force_sale_min_qty(self):
        for rec in self:
            rec.force_sale_min_qty = (
                rec.manual_force_sale_min_qty or rec.force_sale_min_qty_tmpl
            )

    @api.depends("sale_min_qty_tmpl", "manual_sale_min_qty")
    def _compute_sale_min_qty(self):
        for rec in self:
            rec.sale_min_qty = rec.manual_sale_min_qty or rec.sale_min_qty_tmpl

    @api.depends("sale_multiple_qty_tmpl", "manual_sale_multiple_qty")
    def _compute_sale_multiple_qty(self):
        for rec in self:
            rec.sale_multiple_qty = (
                rec.manual_sale_multiple_qty or rec.sale_multiple_qty_tmpl
            )
