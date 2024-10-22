# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def _onchange_product_country_restriction(self):
        """
        Check if there are country restrictions on the product and get warning
        message
        :return: {'warning':...}
        """
        res = {}
        company = self.company_id or self.env.company
        if company.enable_sale_country_restriction:
            restriction_obj = self.env["product.country.restriction"]
            countries = self.order_id.partner_shipping_id.country_id
            restrict_id = self.order_id.partner_shipping_id.country_restriction_id
            if self.product_id and countries:
                restrictions = self.product_id._get_country_restrictions(
                    countries,
                    restriction_id=restrict_id,
                )

                if restrictions:
                    warning = {"title": _("Product Country Restriction"), "message": ""}
                    messages = restriction_obj._get_country_restriction_messages(
                        restrictions
                    )
                    if messages:
                        warning.update(
                            {"message": "\n".join([warning["message"], messages])}
                        )
                        res.update({"warning": warning})
        return res
