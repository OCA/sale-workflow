# Copyright 2021 Camptocamp SA
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.product_seasonality.tests.common import CommonCaseWithLines


class CommonCase(CommonCaseWithLines):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
