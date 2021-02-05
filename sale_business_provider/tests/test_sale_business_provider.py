# © 2021 Akretion (Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestSaleBusinessProvider(common.TransactionCase):
    def setUp(self):
        super(TestSaleBusinessProvider, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        self.sale_report_model = self.env["sale.report"]
        self.sale_order = self.env.ref("sale.sale_order_4")
        self.business_provider = self.env.ref("base.res_partner_5")

    def test_sale_business_provider(self):
        self.sale_order.business_provider = self.business_provider
        self.assertEqual(
            self.sale_order.business_provider,
            self.business_provider,
        )
        sale_line_report = self.sale_report_model.search(
            [
                ("business_provider_id", "=", self.business_provider.id),
            ],
        )
        self.assertEqual(len(self.sale_order.sale_line), len(sale_line_report))
