# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductSetLine(models.Model):
    _inherit = 'product.set.line'

    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
        # made it required false here and required true in view,
        # as it was producing an error in runbot, because of
        # sale_product_set_layout creating
        # demo data without templates
        required=False,
    )
    product_variant_ids = fields.Many2many(
        'product.product',
        domain="""[
            '&',
            ('sale_ok', '=', True),
            ('product_tmpl_id', '=', product_template_id),
        ]""",
        string='Variant',
        required=False,
    )
    product_id = fields.Many2one(
        required=False,
    )
