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

    _inherit = "sale.order"

    check_blacklist_countries = fields.Boolean(
        compute='_compute_check_blacklist_countries',
    )
    country_blacklisted_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_country_blacklisted_product_ids',
    )
    country_blacklisted_category_ids = fields.Many2many(
        'product.category',
        compute='_compute_country_blacklisted_category_ids',
    )
    filtered_country_blacklist_products = fields.Many2many(
        'product.product',
        compute='_compute_filtered_country_blacklist_products',
        help="Here are products that are taken into account for"
             "country blacklisting"
    )

    @api.multi
    def _get_filtered_country_blacklist_products(self):
        self.ensure_one()
        res = self.order_line.mapped('product_id')
        return res

    @api.multi
    @api.depends('order_line.product_id')
    def _compute_filtered_country_blacklist_products(self):
        """
        This method  filter products before evaluating
        blacklist conditions. This can be overridden
        :return:
        """
        for order in self:
            products = order._get_filtered_country_blacklist_products()
            order.filtered_country_blacklist_products = products

    @api.multi
    @api.onchange("partner_shipping_id", "partner_id")
    def onchange_partners_check_country(self):
        res = {}
        for partner in (self.partner_id, self.partner_shipping_id):
            if partner and not partner.country_id:
                warning = (
                    _(u"The country of the partner %s must be set")
                    % self.partner_shipping_id.display_name
                )
                res = _append_warning(res, warning)
        return res

    @api.multi
    @api.depends(
        'product_id.blacklisted_category_country_ids',
        'partner_id.country_id',
        'partner_shipping_id.country_id')
    def _compute_country_blacklisted_category_ids(self):
        for order in self:
            partner_countries = (
                order.partner_id.country_id &
                order.partner_shipping_id.country_id
            )
            products = order.filtered_country_blacklist_products
            order.country_blacklisted_category_ids = products.mapped(
                'blacklisted_category_country_ids').filtered(
                    lambda c: any(
                        country.id in partner_countries.ids
                        for country in c.blacklisted_countries_ids))

    @api.multi
    @api.depends(
        'country_blacklisted_category_ids',
        'order_line.product_id.tmpl_blacklisted_countries_ids',
        'order_line.product_id.tmpl_globally_allowed')
    def _compute_check_blacklist_countries(self):
        """
        We check if sale order contains products configured with blacklist
        countries
        :return:
        """
        for order in self.filtered(
                lambda o: (
                    any(not p.tmpl_globally_allowed and
                        p.tmpl_blacklisted_countries_ids
                        for p in o.filtered_country_blacklist_products) or
                    any(p.var_blacklisted_countries_ids
                        for p in o.filtered_country_blacklist_products) or
                    o.country_blacklisted_category_ids)):
            order.check_blacklist_countries = True

    @api.multi
    @api.depends(
        'check_blacklist_countries',
        'partner_shipping_id.country_id',
        'partner_id.country_id')
    def _compute_country_blacklisted_product_ids(self):
        for order in self.filtered(
                lambda o: o.check_blacklist_countries and
                (o.partner_id.country_id or o.partner_shipping_id.country_id)):
            country_ids = order.partner_id.country_id |\
                order.partner_shipping_id.country_id
            products = order.filtered_country_blacklist_products.\
                filtered(
                    lambda p, c_ids=country_ids: (
                        not p.tmpl_globally_allowed and
                        p.tmpl_blacklisted_countries_ids in c_ids) or
                    p.var_blacklisted_countries_ids in c_ids)
            order.country_blacklisted_product_ids = products

    @api.multi
    def check_countries_blacklisted(self):
        for order in self.filtered('check_blacklist_countries'):
            if not order.partner_id.country_id:
                error = (
                    _(u"The country of the partner %s must be set")
                    % order.partner_id.display_name
                )
                raise ValidationError(error)
            if not order.partner_shipping_id.country_id:
                error = (
                    _(u"The country of the shipping partner %s must be set")
                    % order.partner_shipping_id.display_name
                )
                raise ValidationError(error)
            if order.country_blacklisted_product_ids:
                msg = _(
                    "The following products are banned from being sold "
                    "of the country of the partner or shipping address: "
                )
                msg += u", ".join(p.display_name for p in
                                  order.country_blacklisted_product_ids)
                raise ValidationError(msg)

            category_ids = order.country_blacklisted_category_ids
            if category_ids:
                msg = _(
                    "The following product categories are banned from "
                    "being sold to the country of the partner or "
                    "shipping address: "
                )
                msg += u", ".join(c.display_name for c in category_ids)
                raise ValidationError(msg)

    @api.multi
    def action_confirm(self):
        self.check_countries_blacklisted()
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def onchange_product_check_blacklist(self):
        res = {}
        if self.product_id and (self.order_id.partner_id or
                                self.order_id.partner_shipping_id):
            warning = {
                'warning': {'title': _('Country restriction'),
                            'message': _("This product cannot be sold to the "
                                         "selected country/countries)")},
            }
            if self.product_id in\
                    self.order_id.country_blacklisted_product_ids:
                return warning
            partner_countries = self.order_id.partner_id.country_id | \
                self.order_id.partner_shipping_id.country_id
            if self.env["product.category"].search([
                    ('id', 'parent_of', self.product_id.categ_id.id),
                    ("blacklisted_countries_ids", "in",
                     partner_countries.ids)]):
                return warning
        return res
