# -*- coding: utf-8 -*-
# Copyright 2018  Acsone SA/NV (http://www.acsone.eu)
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from collections import defaultdict
from operator import attrgetter

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SalePromotionRule(models.Model):
    _name = 'sale.promotion.rule'
    _description = 'Sale Promotion Rule'

    sequence = fields.Integer(default=10)
    rule_type = fields.Selection(
        selection=[
            ('coupon', 'Coupon'),
            ('auto', 'Automatic'),
            ],
        required=True,
        default='coupon')
    name = fields.Char(required=True,
                       translate=True)
    code = fields.Char()
    discount_amount = fields.Float(
        digits=dp.get_precision('Discount'),
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
            ('amount_tax_included', 'Amount (Taxes included)'),
            ('amount_tax_excluded', 'Amount (Taxes excluded)'),
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
    minimal_amount = fields.Float(
        digits=dp.get_precision('Discount'))
    is_minimal_amount_tax_incl = fields.Boolean(
        "Tax included into minimal amount?",
        default=True,
        required=True)
    multi_rule_strategy = fields.Selection(
        selection=[
            ('use_best', 'Use the best promotion'),
            ('cumulate', 'Cumulate promotion'),
            ('exclusive', 'Exclusive promotion'),
            ('keep_existing', 'Keep existing discount'),
        ],
        default='use_best',
        description="""
It's possible to apply multiple promotions to a sale order. In such a case
the rules will be applied in the sequence order.
If the first applicable rule is 'exclusice' the process will only apply
this rule. Otherwise the process will loop over each rule and apply it
according to the strategy
"""
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE (code)', _('Discount code must be unique !'))]

    def _get_lines_excluded_from_total_amount(self, order):
        return self.env['sale.order.line'].browse()

    def _check_valid_partner_list(self, order):
        self.ensure_one()
        return not self.restrict_partner_ids\
            or order.partner_id.id in self.restrict_partner_ids.ids

    def _check_valid_pricelist(self, order):
        self.ensure_one()
        return not self.restrict_pricelist_ids\
            or order.pricelist_id.id in self.restrict_pricelist_ids.ids

    def _check_valid_newsletter(self, order):
        self.ensure_one()
        return not self.only_newsletter or not order.partner_id.opt_out

    def _check_valid_date(self, order):
        self.ensure_one()
        return not (
            (self.date_to and fields.Date.today() > self.date_to) or
            (self.date_from and fields.Date.today() < self.date_from))

    def _check_valid_total_amount(self, order):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Discount')
        excluded_lines = self._get_lines_excluded_from_total_amount(order)
        included_lines = order.order_line - excluded_lines
        amount = 0
        for line in included_lines:
            # we need to ignore already applied promotions
            taxes = line.tax_id.compute_all(
                line.price_unit, line.order_id.currency_id,
                line.product_uom_qty, product=line.product_id,
                partner=line.order_id.partner_shipping_id)
            if self.is_minimal_amount_tax_incl:
                amount += taxes['total_included']
            else:
                amount += taxes['total_excluded']
        return float_compare(
            self.minimal_amount,
            amount,
            precision_digits=precision) < 0

    def _check_valid_usage(self, order):
        self.ensure_one()
        if self.usage_restriction == 'one_per_partner':
            return not self.env['sale.order'].search_count([
                ('id', '!=', order.id),
                ('partner_id', '=', order.partner_id.id),
                ('promotion_rule_id', '=', self.id),
                ('state', '!=', 'cancel')])
        return True

    def _check_valid_multi_rule_strategy(self, order):
        self.ensure_one()
        if self.multi_rule_strategy == 'exclusive':
            return not order.applied_promotion_rule_ids
        return True

    def _check_valid_rule_type(self, order):
        self.ensure_one()
        if self.rule_type == 'coupon':
            return order.coupon_code is False
        return True

    @api.model
    def _get_restrictions(self):
        return [
            'date',
            'total_amount',
            'partner_list',
            'pricelist',
            'newsletter',
            'usage',
            'rule_type',
            'multi_rule_strategy']

    def _is_promotion_valid(self, order):
        self.ensure_one()
        restrictions = self._get_restrictions()
        for key in restrictions:
            if not getattr(self, '_check_valid_%s' % key)(order):
                _logger.debug('Invalid restriction %s', key)
                return False
        return True

    def _is_promotion_valid_for_line(self, line):
        precision = self.env['decimal.precision'].precision_get('Discount')
        if self.multi_rule_strategy == 'cumulate':
            return True
        if line.discount and self.multi_rule_strategy == 'use_best':
            return float_compare(
                self.discount_amount,
                line.discount,
                precision_digits=precision) > 0
        if self.multi_rule_strategy == 'keep_existing':
            return not line.discount
        return True

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.rule_type == 'coupon':
                res.append(
                    (record.id, u'%s (%s)' % (record.name, record.code))
                )
            elif record.rule_type == 'auto':
                res.append(
                    (record.id, u'%s (%s)' % (record.name, _('Automatic')))
                )
            else:
                res.extend(
                    super(SalePromotionRule, record)._name_get()
                )
        return res

    @api.model
    def compute_promotions(self, orders):
        """
        Compute available promotions on the given orders. If a coupon is
        already defined on the orders, it's preserved
        """
        orders_by_coupon = defaultdict(self.env['sale.order'].browse)
        for order in orders:
            orders_by_coupon[order.coupon_promotion_rule_id] += order
        # first reset
        self.remove_promotions(orders)
        for coupon, _orders in orders_by_coupon.items():
            # coupon must be always applied first
            if coupon:
                coupon._apply(orders)
            self.apply_auto(orders)

    @api.multi
    def apply_coupon(self, orders, coupon_code):
        """Add a coupon to orders"""
        coupon_rule = self.search([
            ('code', '=ilike', coupon_code),
            ('rule_type', '=', 'coupon'),
        ])
        if not coupon_rule:
            raise UserError(
                _('Code number %s is invalid') % coupon_code)
        orders_without_coupon = orders.filtered(
            lambda o, c=coupon_rule: o.coupon_promotion_rule_id != coupon_rule)
        self.remove_promotions(orders_without_coupon)
        # coupon take precedence on auto rules
        coupon_rule._apply(orders_without_coupon)
        self.apply_auto(orders_without_coupon)

    @api.model
    def apply_auto(self, orders):
        """Apply automatic promotion rules to the orders"""
        auto_rules = self.search([
            ('rule_type', '=', 'auto'),
        ])
        auto_rules._apply(orders)

    @api.model
    def remove_promotions(self, orders):
        orders.write({
            'promotion_rule_ids': [(5,)],
            'coupon_promotion_rule_id': False
        })
        self._remove_promotions_lines(orders.mapped('order_line'))

    @api.model
    def _remove_promotions_lines(self, lines):
        lines_by_order = defaultdict(self.env['sale.order.line'].browse)
        for line in lines:
            lines_by_order[line.order_id] |= line
        # update lines from the order to avoid to trigger the compute
        # methods on each line updated. Indeed, update on a X2many field
        # is always done in norecompute on the parent...
        for order, _lines in lines_by_order.items():
            vals = []
            for line in _lines:
                if not line.has_promotion_rules:
                    continue
                v = {
                    'discount': 0.0,
                    'coupon_promotion_rule_id': False,
                    'promotion_rule_ids': [(5,)]
                }
                vals.append((1, line.id, v))
            if vals:
                order.write({'order_line': vals})

    @api.multi
    def _apply(self, orders):
        for rule in self:
            orders = orders.filtered(
                lambda o, r=rule: r._is_promotion_valid(o))
            rule._apply_rule_to_order_lines(orders.mapped('order_line'))
            if rule.rule_type == 'coupon':
                orders.write({'coupon_promotion_rule_id': rule.id})
            else:
                orders.write({'promotion_rule_ids': [(4, rule.id)]})

    @api.multi
    def _apply_rule_to_order_lines(self, lines):
        self.ensure_one()
        lines = lines.filtered(
            lambda l, r=self: r._is_promotion_valid_for_line(l))
        if self.promo_type == 'discount':
            self._apply_discount_to_order_lines(lines)
        else:
            raise ValidationError(
                _('Not supported promotion type %s') % self.promo_type
            )

    def _compute_percent_amount_tax_exc(self, order, lines):
        percent_discount = (
            100.0 - (
                (order.amount_untaxed - self.discount_amount)
                / order.amount_untaxed
                * 100.0
            )
        )
        return dict.fromkeys(lines, percent_discount)

    def _compute_percent_amount_tax_inc(self, order, lines):
        average_discount = (
            100.0 - (
                (order.amount_total - self.discount_amount)
                / order.amount_total
                * 100.0
            )
        )
        return dict.fromkeys(lines, average_discount)

    def _compute_percent_discount_by_lines(self, order, lines):
        self.ensure_one()
        if not order == lines.mapped('order_id'):
            raise Exception("All lines must come from the same order")

        if self.discount_type == "amount_tax_excluded":
            percent_by_line = self._compute_percent_amount_tax_exc(
                order, lines
            )
        elif self.discount_type == "amount_tax_included":
            percent_by_line = self._compute_percent_amount_tax_inc(
                order, lines
            )
        elif self.discount_type == "percentage":
            percent_by_line = dict.fromkeys(lines, self.discount_amount)
        else:
            raise ValidationError(
                _('Discount promotion of type %s is not supported') %
                self.discount_type
            )
        return percent_by_line

    @api.multi
    def _get_snapshot_before_apply_discount(self, order, lines):
        """ Takes a snapshop of informations before applying the discount.
        This snapshop is then passed to the `_finaly_apply_discount` method
        once the rule is applied.
        :param order:
        :param lines:
        :return: a dictionary of informations to preserve before applying the
        discount.
        """
        self.ensure_one()
        return {
            'amount_total': order.amount_total,
            'amount_untaxed': order.amount_untaxed
        }

    def _finalyse_apply_discount(self, order, lines, snapshop_info):
        """ This method is called after the current promotion rule has been
        applied.
        :param order:
        :param lines:
        :param snapshop_info:
        :return:
        """
        self.ensure_one()
        # for disount based on amountwe must be sure that the final discount
        # is the one expected since the amount can differ due to the rounding
        # of the discount on each line
        if self.discount_type not in (
                "amount_tax_excluded", "amount_tax_included"):
            return
        if self.discount_type == "amount_tax_excluded":
            applied_amount = (
                    snapshop_info['amount_untaxed'] - order.amount_untaxed)
        else:
            applied_amount = (
                    snapshop_info['amount_total'] - order.amount_total)
        precision = self.env['decimal.precision'].precision_get('Discount')
        applied_amount_diff = self.discount_amount - applied_amount
        if float_is_zero(applied_amount_diff, precision_digits=precision):
            return

        # we must add an additional discount on one line to ensure that the
        # applied discount is the amount expected
        price_precision_digits = self.env[
            'decimal.precision'].precision_get('Product Price')
        for line in order.order_line:
            # we iter on all line while we have a diff between the applied
            # discount and the expected one
            if float_is_zero(
                    line.price_unit,
                    precision_digits=price_precision_digits):
                # we ignore line with price = 0
                continue
            line_amount_getter = attrgetter('price_total')
            if self.discount_type == "amount_tax_excluded":
                line_amount_getter = attrgetter('price_subtotal')
            line_amount = line_amount_getter(line)
            additional_discount = (
                100.0 - (
                    (line_amount - applied_amount_diff)
                    / line_amount
                    * 100.0
                )
            )
            if not float_is_zero(
                    additional_discount, precision_digits=precision):
                # we've found a candidate line. We apply an additional discount
                line.discount += additional_discount
                new_line_amount = line_amount_getter(line)
                # we compute the remaining amount to deduce once the discount
                # has been changed
                applied_amount_diff = new_line_amount - line_amount
                if float_is_zero(
                        applied_amount_diff,
                        precision_digits=price_precision_digits):
                    # no more amount to deduce
                    return

    @api.multi
    def _apply_discount_to_order_lines(self, lines):
        self.ensure_one()
        if not self.promo_type == 'discount':
            return

        lines_by_order = defaultdict(self.env['sale.order.line'].browse)
        for line in lines:
            lines_by_order[line.order_id] |= line
        # update lines from the order to avoid to trigger the compute
        # methods on each line updated. Indeed, update on a X2many field
        # is always done in norecompute on the parent...
        for order, _lines in lines_by_order.items():
            #original_values = order.conver_to_read
            discount_by_line = self._compute_percent_discount_by_lines(
                order, lines)
            snapshop_info = self._get_snapshot_before_apply_discount(
                order, lines)
            vals = []
            for line in _lines:
                percent_discount = discount_by_line[line]
                discount = line.discount
                if self.multi_rule_strategy != 'cumulate':
                    discount = 0.0
                discount += percent_discount
                if self.rule_type == 'coupon':
                    v = {
                        'discount': discount,
                        'coupon_promotion_rule_id': self.id
                    }
                else:
                    v = {
                        'discount': discount,
                        'promotion_rule_ids': [(4, self.id)]
                    }
                vals.append((1, line.id, v))
            if vals:
                order.write({'order_line': vals})
            self._finalyse_apply_discount(order, lines, snapshop_info)
