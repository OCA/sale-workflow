# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


def _append_warning(res, new_message):
    if not res:
        res = {}
    if res.get("warning"):
        res["warning"]["message"] += u"\n" + new_message
    else:
        res["warning"] = {
            "title": _("Warning"),
            "message": new_message,
        }
    return res


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    country_restriction_id = fields.Many2one(
        comodel_name='product.country.restriction',
        related='partner_shipping_id.country_restriction_id',
        string='Country Restriction',
        readonly=True,
    )

    @api.multi
    def _check_partner_shipping_country_restriction(self):
        """
        Country Restriction on Partner is mandatory
        :return:
        """
        for partner in self.mapped('partner_shipping_id'):
            if partner and not partner.country_restriction_id:
                raise ValidationError(
                    _("The Country Restriction of the partner %s must be set")
                    % self.partner_shipping_id.display_name
                )

    @api.multi
    def _get_country_restriction_products_to_check(self):
        """
        This is a hook if one wants to filter checked products
        :return:
        """
        self.ensure_one()
        return self.order_line.mapped('product_id')

    @api.multi
    def check_country_restriction(self):
        restriction_obj = self.env['product.country.restriction']
        self._check_partner_shipping_country_restriction()
        for order in self:
            countries = order.partner_shipping_id.country_id
            products = order._get_country_restriction_products_to_check()
            restrictions = products._get_country_restrictions(
                countries,
                restriction_id=order.country_restriction_id
            )
            if restrictions:
                messages = restriction_obj._get_country_restriction_messages(
                    restrictions)
                if messages:
                    raise ValidationError(messages)

    @api.multi
    def action_confirm(self):
        self.check_country_restriction()
        return super(SaleOrder, self).action_confirm()

    @api.multi
    @api.onchange("partner_shipping_id")
    def _onchange_partners_check_country(self):
        res = {}
        for partner in self.mapped('partner_shipping_id'):
            if partner and not partner.country_id:
                warning = (
                    _(u"The country of the partner %s must be set")
                    % self.partner_shipping_id.display_name
                )
                res = _append_warning(res, warning)
        return res
