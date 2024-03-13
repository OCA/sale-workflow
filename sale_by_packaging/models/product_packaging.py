from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    can_be_sold = fields.Boolean(
        string="Can be sold", compute="_compute_can_be_sold", readonly=False, store=True
    )
    sale_rounding = fields.Float(
        string="Sale Rounding Precision",
        digits="Product Unit of Measure",
        required=True,
        default=0.1,
        help="The allowed package quantity will be a multiple of this value. "
        "Use 1.0 for a package that cannot be further split.",
    )

    @api.depends("packaging_level_id")
    def _compute_can_be_sold(self):
        for record in self:
            record.can_be_sold = record.packaging_level_id.can_be_sold
