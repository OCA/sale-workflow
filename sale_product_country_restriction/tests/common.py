# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product_country_restriction.tests.common\
    import CountryRestrictionCommon


class SaleCountryRestrictionCommon(CountryRestrictionCommon):

    def setUp(self):
        super(SaleCountryRestrictionCommon, self).setUp()
        self.line_obj = self.env['sale.order.line']

        vals = {
            'name': 'Partner Korea',
            'country_id': self.kp.id,
            'country_restriction_id': self.restriction_2.id,
        }
        self.partner = self.env['res.partner'].create(vals)
        vals = {
            'partner_id': self.partner.id,
        }

        self.sale_order = self.env['sale.order'].create(vals)
        # Enable restriction behaviour
        self.env.user.company_id.enable_sale_country_restriction = True
