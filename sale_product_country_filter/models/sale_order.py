# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import threading

from odoo import api, models, _
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
    def check_blacklist(self):
        for order in self:
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

            partner_countries = (
                order.partner_id.country_id &
                order.partner_shipping_id.country_id
            )
            partner_countries_ids = partner_countries.ids

            order_products = order.order_line.mapped("product_id")
            flagged_products = self.env["product.product"].search(
                [
                    ("id", "in", order_products.ids),
                    "|",
                    "&",
                    ("tmpl_globally_allowed", "=", False),
                    (
                        "tmpl_blacklisted_countries_ids",
                        "in",
                        partner_countries_ids,
                    ),
                    (
                        "var_blacklisted_countries_ids",
                        "in",
                        partner_countries_ids,
                    ),
                ]
            )
            if flagged_products:
                msg = _(
                    "The following products are banned from being sold "
                    "of the country of the partner or shipping address: "
                )
                msg += u", ".join(p.display_name for p in flagged_products)
                raise ValidationError(msg)

            direct_categories = order_products.mapped("categ_id")
            flagged_categories = self.env["product.category"].search(
                [
                    ("id", "parent_of", direct_categories.ids),
                    ("blacklisted_countries_ids", "in", partner_countries_ids),
                ]
            )
            if flagged_categories:
                msg = _(
                    "The following product categories are banned from "
                    "being sold to the country of the partner or "
                    "shipping address: "
                )
                msg += u", ".join(c.display_name for c in flagged_categories)
                raise ValidationError(msg)

    @api.multi
    def action_confirm(self):
        test_mode = getattr(threading.currentThread(), 'testing', False)
        testing_current_module = self.env.context.get(
            'testing_sale_product_country_filter')
        if not test_mode or testing_current_module:
            self.check_blacklist()
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def onchange_product_check_blacklist(self):
        if self.product_id and (self.order_id.partner_id or
                                self.order_id.partner_shipping_id):
            warning = {
                'warning': _("This product cannot be sold to the selected "
                             "country/countries)"),
            }
            prod = self.product_id
            partner_countries = (
                self.order_id.partner_id.country_id &
                self.order_id.partner_shipping_id.country_id
            )
            blacklisted_template = (
                not prod.tmpl_globally_allowed and
                partner_countries & prod.tmpl_blacklisted_countries_ids
            )
            blacklisted_variant = (
                partner_countries & prod.var_blacklisted_countries_ids
            )

            if blacklisted_template or blacklisted_variant:
                return warning

            flagged_categories = self.env["product.category"].search(
                [
                    ("id", "parent_of", prod.categ_id.id),
                    ("blacklisted_countries_ids", "in",
                     partner_countries.ids),
                ], limit=1
            )
            if flagged_categories:
                return warning
