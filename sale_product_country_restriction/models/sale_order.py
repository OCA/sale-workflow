# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def _append_warning(res, new_message):
    if not res:
        res = {}
    if res.get("warning"):
        res["warning"]["message"] += "\n" + new_message
    else:
        res["warning"] = {
            "title": _("Warning"),
            "message": new_message,
        }
    return res


class SaleOrder(models.Model):

    _inherit = "sale.order"

    country_restriction_id = fields.Many2one(
        comodel_name="product.country.restriction",
        related="partner_shipping_id.country_restriction_id",
        string="Country Restriction",
        readonly=True,
    )

    @api.model
    def _get_no_country_restriction_partner_message(self, partner):
        return _("The country of the partner %s must be set") % partner.display_name

    @api.model
    def _get_no_restriction_partner_message(self, partner):
        self.ensure_one()
        return (
            _("A country restriction of the partner %s must be set")
            % partner.display_name
        )

    def _check_partner_shipping_country_restriction(self):
        """
        Country Restriction on Partner is mandatory
        :return:
        """
        for partner in self.mapped("partner_shipping_id"):
            if partner and not partner.country_restriction_id:
                raise ValidationError(
                    self._get_no_country_restriction_partner_message(partner)
                )
            if partner and not partner.country_id:
                raise ValidationError(self._get_no_restriction_partner_message(partner))

    def _get_country_restriction_products_to_check(self):
        """
        This is a hook if one wants to filter checked products
        :return:
        """
        self.ensure_one()
        return self.order_line.mapped("product_id")

    def check_country_restriction(self):
        restriction_obj = self.env["product.country.restriction"]
        self._check_partner_shipping_country_restriction()
        for order in self:
            countries = order.partner_shipping_id.country_id
            products = order._get_country_restriction_products_to_check()
            restrictions = products._get_country_restrictions(
                countries, restriction_id=order.country_restriction_id
            )
            if restrictions:
                messages = restriction_obj._get_country_restriction_messages(
                    restrictions
                )
                if messages:
                    raise ValidationError(messages)

    def action_confirm(self):
        for rec in self:
            if rec.company_id.enable_sale_country_restriction:
                rec.check_country_restriction()
        return super().action_confirm()

    @api.onchange("partner_shipping_id")
    def _onchange_partners_check_country(self):
        res = {}
        company = self.company_id or self.env.company
        if company.enable_sale_country_restriction:
            for partner in self.mapped("partner_shipping_id"):
                if partner and not partner.country_id:
                    warning = (
                        _("The country of the partner %s must be set")
                        % self.partner_shipping_id.display_name
                    )
                    res = _append_warning(res, warning)
        return res

    @api.onchange("partner_shipping_id", "company_id")
    def _onchange_partners_check_restriction(self):
        res = {}
        if not self.company_id or not self.company_id.enable_sale_country_restriction:
            return res
        for partner in self.mapped("partner_shipping_id"):
            if partner and not partner.country_restriction_id:
                warning = self._get_no_restriction_partner_message(partner)
                res = _append_warning(res, warning)
        return res
