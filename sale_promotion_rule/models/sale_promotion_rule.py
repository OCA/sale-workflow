# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class SalePromotionRule(models.Model):
    _name = 'sale.promotion.rule'
    _description = 'Sale Promotion Rule'
    _rec_name = "display_name"

    sequence = fields.Integer('Sequence', default=10)
    rule_type = fields.Selection(
        selection=[
            ('coupon', 'Coupon'),
            ('auto', 'Automatic'),
            ],
        string='Rule type',
        required=True,
        default='coupon')
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    discount_amount = fields.Float(
        string='Discount amount',
        digits_compute=dp.get_precision('Account'),
        required=True)
    promo_type = fields.Selection(
        selection=[
            # ('gift', 'Gift'), TODO implement
            ('discount', 'Discount'),
            ],
        required=True,
        default='discount')
    discount_type = fields.Selection(
        selection=[
            ('percentage', 'Percentage'),
            # ('amount', 'Amount'), TODO implement
            ],
        required=True,
        default='percentage')
    date_from = fields.Date()
    date_to = fields.Date()
    only_newsletter = fields.Boolean()
    restrict_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='discount_rule_partner_rel',
        column1='rule_id',
        column2='partner_id',
        string='Restricted partners')
    restrict_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        relation='discount_rule_pricelist_rel',
        column1='rule_id',
        column2='pricelist_id',
        string='Restricted pricelists')
    usage_restriction = fields.Selection(
        selection=[
            ('one_per_partner', 'One per partner'),
            ('no_restriction', 'No restriction')
        ], default='no_restriction',
        required=True)
    restriction_amount = fields.Selection(
        selection=[
            ('amount_total', 'Taxed amount'),
            ('amount_untaxed', 'Untaxed amount'),
        ], default='amount_total',
        required=True)
    minimal_amount = fields.Float(
        string='Minimal amount',
        digits_compute=dp.get_precision('Account'))
    display_name = fields.Char(
        compute='_compute_display_name')
    use_best_discount = fields.Boolean(String='Use best discount')

    _sql_constraints = [
        ('code_unique', 'UNIQUE (code)', _('Discount code must be unique !'))]

    def _check_valid_partner_list(self, order):
        return not self.restrict_partner_ids\
            or order.partner_id.id in self.restrict_partner_ids.ids

    def _check_valid_pricelist(self, order):
        return not self.restrict_pricelist_ids\
            or order.pricelist_id.id in self.restrict_pricelist_ids.ids

    def _check_valid_newsletter(self, order):
        return not self.only_newsletter or not order.partner_id.opt_out

    def _check_valid_date(self, order):
        return not (
            (self.date_to and fields.Date.today() > self.date_to) or
            (self.date_from and fields.Date.today() < self.date_from))

    def _check_valid_total_amount(self, order):
        return self.minimal_amount < order[self.restriction_amount]

    def _check_valid_usage(self, order):
        if self.usage_restriction == 'one_per_partner':
            return not self.env['sale.order'].search([
                ('id', '!=', order.id),
                ('partner_id', '=', order.partner_id.id),
                ('promotion_rule_id', '=', self.id),
                ('state', '!=', 'cancel')])
        else:
            return True

    def _is_promotion_valid(self, order):
        restrictions = [
            'date',
            'total_amount',
            'partner_list',
            'pricelist',
            'newsletter',
            'usage',
            ]
        for key in restrictions:
            if not getattr(self, '_check_valid_%s' % key)(order):
                _logger.debug('Invalid restriction %s', key)
                return False
        return True

    def _compute_display_name(self):
        for record in self:
            if record.rule_type == 'coupon':
                record.display_name = '%s (%s)' % (record.name, record.code)
            elif record.rule_type == 'auto':
                record.display_name = '%s (%s)' % (record.name, 'Automatic')
            else:
                super(SalePromotionRule, record)._compute_display_name()
