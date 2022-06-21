from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_uom_id = fields.Many2one("uom.uom", "Default Sale UoM")
    uom_category_id = fields.Many2one(
        "uom.category", related="uom_id.category_id", string="UOM Category"
    )

    @api.onchange("uom_id")
    def remove_sale_uom(self):
        for rec in self:
            rec.sale_uom_id = False
