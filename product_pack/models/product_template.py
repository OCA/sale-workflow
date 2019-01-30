##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # TODO rename a pack_type
    pack_price_type = fields.Selection([
        ('components_price', 'Detailed - Components Prices'),
        ('totalice_price', 'Detailed - Totaliced Price'),
        ('fixed_price', 'Detailed - Fixed Price'),
        ('none_detailed_assited_price', 'None Detailed - Assisted Price'),
        ('none_detailed_totaliced_price', 'None Detailed - Totaliced Price'),
    ],
        'Pack Type',
        help="* Detailed - Components Prices: Detail lines with prices on "
        "sales order.\n"
        "* Detailed - Totaliced Price: Detail lines on sales order totalicing "
        "lines prices on pack (don't show component prices).\n"
        "* Detailed - Fixed Price: Detail lines on sales order and use product"
        " pack price (ignore line prices).\n"
        "* None Detailed - Assisted Price: Do not detail lines on sales "
        "order. Assist to get pack price using pack lines."
    )
    pack = fields.Boolean(
        'Pack?',
        help='Is a Product Pack?',
    )
    pack_line_ids = fields.One2many(
        related='product_variant_ids.pack_line_ids',
        readonly=True,
    )
    used_pack_line_ids = fields.One2many(
        related='product_variant_ids.used_pack_line_ids',
        readonly=True,
    )
    allow_modify_pack = fields.Boolean(
    )

    @api.constrains(
        'product_variant_ids', 'pack_price_type')
    def check_relations(self):
        """
        Check assited packs dont have packs a childs
        """
        # check assited price has no packs child of them
        for rec in self:
            if rec.pack_price_type == 'none_detailed_assited_price':
                child_packs = rec.mapped(
                    'pack_line_ids.product_id').filtered('pack')
                if child_packs:
                    raise ValidationError(_(
                        'A "None Detailed - Assisted Price Pack" can not have '
                        'a pack as a child!'))

        # TODO we also should check this
        # check if we are configuring a pack for a product that is partof a
        # assited pack
        # if self.pack:
        #     for product in self.product_variant_ids
        #     parent_assited_packs = self.env['product.pack.line'].search([
        #         ('product_id', '=', self.id),
        #         ('parent_product_id.pack_price_type', '=',
        #             'none_detailed_assited_price'),
        #         ])
        #     print 'parent_assited_packs', parent_assited_packs
        #     if parent_assited_packs:
        #         raise Warning(_(
        #             'You can not set this product as pack because it is part'
        #             ' of a "None Detailed - Assisted Price Pack"'))

    @api.constrains('company_id', 'product_variant_ids')
    def check_pack_line_company(self):
        """
        Check packs are related to packs of same company
        """
        for rec in self:
            for line in rec.pack_line_ids:
                if line.product_id.company_id != rec.company_id:
                    raise ValidationError(_(
                        'Pack lines products company must be the same as the '
                        'parent product company'))
            for line in rec.used_pack_line_ids:
                if line.parent_product_id.company_id != rec.company_id:
                    raise ValidationError(_(
                        'Pack lines products company must be the same as the '
                        'parent product company'))

    @api.multi
    def write(self, vals):
        """
        We remove from prod.prod to avoid error
        """
        if vals.get('pack_line_ids', False):
            self.product_variant_ids.write(
                {'pack_line_ids': vals.pop('pack_line_ids')})
        return super(ProductTemplate, self).write(vals)
