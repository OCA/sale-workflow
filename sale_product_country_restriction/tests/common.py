# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.product_country_restriction.tests.common import (
    CountryRestrictionCommon,
)


class SaleCountryRestrictionCommon(CountryRestrictionCommon):
    def setUp(self):
        super().setUp()
        self.line_obj = self.env["sale.order.line"]

        vals = {
            "name": "Partner Korea",
            "country_id": self.kp.id,
            "country_restriction_id": self.restriction_2.id,
        }
        self.partner = self.env["res.partner"].create(vals)
        vals = {
            "partner_id": self.partner.id,
        }

        self.sale_order = self._create_so(partner=self.partner, product=self.product_2)
        # Enable restriction behaviour
        self.env.company.enable_sale_country_restriction = True

    def _create_so(self, partner, product, partner_shipping=None):

        SaleOrder = self.env["sale.order"]

        order_form = Form(SaleOrder)
        order_form.partner_id = partner
        with order_form.order_line.new() as line:
            line.name = product.product_variant_id.name
            line.product_id = product.product_variant_id
            line.product_uom_qty = 1.0
        sale_order = order_form.save()

        return sale_order
