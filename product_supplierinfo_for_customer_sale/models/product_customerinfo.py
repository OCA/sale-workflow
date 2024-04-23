from odoo import api, fields, models


class ProductCustomerinfo(models.Model):
    _inherit = "product.customerinfo"

    product_id = fields.Many2one(
        compute="_compute_product_id", readonly=False, store=True
    )

    @api.depends("product_tmpl_id")
    def _compute_product_id(self):
        self.product_id = False
