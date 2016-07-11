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

    theoritical_price = fields.Float(
        string='Theoritical Price', store=True,
        digits=dp.get_precision('Product Price'),
        compute='_compute_theoritical_multi', multi='theoritical_multi')

    theoritical_difference = fields.Float(
        string='Theoritical Difference', store=True,
        digits=dp.get_precision('Product Price'),
        compute='_compute_theoritical_multi', multi='theoritical_multi')

    margin_state = fields.Selection(
        string='Theoritical Price State', store=True,
        selection=MARGIN_STATE_SELECTION,
        compute='_compute_theoritical_multi', multi='theoritical_multi')

    # Compute Section
    @api.multi
    @api.depends(
        'standard_price', 'list_price',
        'margin_classification_id.margin',
        'margin_classification_id.price_round',
        'margin_classification_id.price_surcharge')
    def _compute_theoritical_multi(self):
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
                template.theoritical_price = tools.float_round(
                    template.standard_price * multi,
                    precision_rounding=classification.price_round) +\
                    classification.price_surcharge
            else:
                template.theoritical_price = template.list_price
            difference = (template.list_price - template.theoritical_price)
            if max(difference, -difference) < 10 ** -9:
                difference = 0
            template.theoritical_difference = difference
            if difference < 0:
                template.margin_state = 'cheap'
            elif difference > 0:
                template.margin_state = 'expensive'
            else:
                template.margin_state = 'ok'

    # Custom Section
    @api.multi
    def use_theoritical_price(self):
        for template in self:
            template.list_price = template.theoritical_price
