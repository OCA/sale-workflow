# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, exceptions, tools, _
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    MARGIN_STATE_SELECTION = [
        ('ok', 'Correct Margin'),
        ('cheap', 'Cheaper'),
        ('expensive', 'Too Expensive'),
    ]

    # Columns Section
    margin_classification_id = fields.Many2one(
        comodel_name='product.margin.classification',
        string='Margin Classification')

    theoretical_price = fields.Float(
        string='Theoretical Price', store=True,
        digits=dp.get_precision('Product Price'),
        compute='_compute_theoretical_multi', multi='theoretical_multi')

    theoretical_difference = fields.Float(
        string='Theoretical Difference', store=True,
        digits=dp.get_precision('Product Price'),
        compute='_compute_theoretical_multi', multi='theoretical_multi')

    margin_state = fields.Selection(
        string='Theoretical Price State', store=True,
        selection=MARGIN_STATE_SELECTION,
        compute='_compute_theoretical_multi', multi='theoretical_multi')

    # Compute Section
    @api.multi
    @api.depends(
        'standard_price', 'list_price',
        'margin_classification_id.margin',
        'margin_classification_id.price_round',
        'margin_classification_id.price_surcharge')
    def _compute_theoretical_multi(self):
        for template in self:
            classification = template.margin_classification_id
            if classification:
                multi = 1 + (classification.margin / 100)
                for tax in template.taxes_id:
                    if tax.amount_type != 'percent' or not tax.price_include:
                        raise exceptions.UserError(_(
                            "Unimplemented Feature\n"
                            "The Tax %s is not correctly set for computing"
                            " prices with coefficients for the product %s") % (
                            tax.name, template.name))
                    multi *= 1 + (tax.amount / 100)
                template.theoretical_price = tools.float_round(
                    template.standard_price * multi,
                    precision_rounding=classification.price_round) +\
                    classification.price_surcharge
            else:
                template.theoretical_price = template.list_price
            difference = (template.list_price - template.theoretical_price)
            if max(difference, -difference) < 10 ** -9:
                difference = 0
            template.theoretical_difference = difference
            if difference < 0:
                template.margin_state = 'cheap'
            elif difference > 0:
                template.margin_state = 'expensive'
            else:
                template.margin_state = 'ok'

    # Custom Section
    @api.multi
    def use_theoretical_price(self):
        for template in self:
            template.list_price = template.theoretical_price
