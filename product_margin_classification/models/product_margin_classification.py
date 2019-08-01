# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError
import odoo.addons.decimal_precision as dp


class ProductMarginClassification(models.Model):
    _name = 'product.margin.classification'
    _inherit = 'ir.needaction_mixin'

    # View Section
    @api.model
    def _needaction_count(self, domain=None, context=None):
        return sum(self.search([]).mapped('template_different_price_qty'))

    # Column Section
    name = fields.Char(string='Name', required=True)

    markup = fields.Float(
        string='Markup', required=True, old_name='margin',
        digits=dp.get_precision('Margin Rate'),
        help="Value that help you to compute the sale price, based on your"
        " cost, as defined: Sale Price = (Cost * (1 + Markup))\n"
        "It is computed with the following formula"
        " Markup = (Sale Price - Cost) / Cost")

    profit_margin = fields.Float(
        string='Profit Margin', compute='_compute_profit_margin',
        inverse='_inverse_profit_margin',
        digits=dp.get_precision('Margin Rate'),
        help="Also called 'Net margin' or 'Net Profit Ratio'.\n"
        "It is computed with the following formula"
        " Profit Margin = (Sale Price - Cost) / Sale Price")

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda s: s._default_company_id())

    template_ids = fields.One2many(
        string='Products', comodel_name='product.template',
        inverse_name='margin_classification_id', readonly=True)

    template_qty = fields.Integer(
        string='Products Quantity', compute='_compute_template_qty',
        store=True)

    template_different_price_qty = fields.Integer(
        string='Total Products With Different Price', multi='differente_price',
        store=True, compute='_compute_template_different_price_qty')

    template_cheap_qty = fields.Integer(
        string='Products Cheaper', multi='differente_price',
        store=True, compute='_compute_template_different_price_qty')

    template_expensive_qty = fields.Integer(
        string='Products Too Expensive', multi='differente_price',
        store=True, compute='_compute_template_different_price_qty')

    price_round = fields.Float(
        string='Price Rounding',
        digits_compute=dp.get_precision('Product Price'),
        default=lambda s: s._default_price_round(),
        help="Sets the price so that it is a multiple of this value.\n"
        "Rounding is applied after the margin and before the surcharge.\n"
        "To have prices that end in 9.99, set rounding 1, surcharge -0.01")

    price_surcharge = fields.Float(
        string='Price Surcharge',
        digits_compute=dp.get_precision('Product Price'),
        help="Specify the fixed amount to add or substract(if negative) to"
        " the amount calculated with the discount.")

    # Default Section
    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_price_round(self):
        decimal_obj = self.env['decimal.precision']
        return 10 ** (- decimal_obj.precision_get('Product Price'))

    # constrains Section
    @api.constrains('markup')
    def _check_markup(self):
        for classification in self:
            if classification.markup == -1:
                raise UserError(_("-1 is not a valid Markup."))

    @api.multi
    def _inverse_profit_margin(self):
        pass

    @api.onchange('profit_margin')
    def _onchange_profit_margin(self):
        for classification in self:
            if classification.profit_margin == 1:
                raise UserError(_("1 is not a valid Profit Margin."))
            classification.markup = 1 * (classification.profit_margin / (
                1 - classification.profit_margin))

    # Compute Section
    @api.multi
    @api.depends('markup')
    def _compute_profit_margin(self):
        for classification in self:
            classification.profit_margin = 1 -\
                (1 / (classification.markup + 1))

    @api.multi
    @api.depends('template_ids.theoretical_difference')
    def _compute_template_different_price_qty(self):
        for classification in self:
            classification.template_cheap_qty =\
                classification.template_ids.mapped(
                    'margin_state').count('cheap')
            classification.template_expensive_qty =\
                classification.template_ids.mapped(
                    'margin_state').count('expensive')
            classification.template_different_price_qty =\
                classification.template_expensive_qty +\
                classification.template_cheap_qty

    @api.multi
    @api.depends('template_ids.margin_classification_id')
    def _compute_template_qty(self):
        for classification in self:
            classification.template_qty = len(classification.template_ids)

    # Constraint Section
    @api.multi
    @api.constrains('price_round')
    def _check_price_round(self):
        for classification in self:
            if classification.price_round == 0:
                raise UserError(
                    _("Price Rounding can not be null."))

    # Custom Section
    @api.multi
    def _apply_theoretical_price(self, state_list):
        template_obj = self.env['product.template']
        for classification in self:
            templates = template_obj.search([
                ('margin_classification_id', '=', classification.id),
                ('margin_state', 'in', state_list)])
            templates.use_theoretical_price()

    @api.multi
    def apply_theoretical_price(self):
        self._apply_theoretical_price(['cheap', 'expensive'])

    @api.multi
    def apply_theoretical_price_cheap(self):
        self._apply_theoretical_price(['cheap'])

    @api.multi
    def apply_theoretical_price_expensive(self):
        self._apply_theoretical_price(['expensive'])
