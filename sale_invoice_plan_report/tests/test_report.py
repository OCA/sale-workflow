# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.sale.tests import common


@tagged("post_install", "-at_install")
class TestSaleInvoicePlanReport(common.TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "name": cls.product_a.name,
                            "product_uom_qty": 2.0,
                            "price_unit": 100.0,
                        },
                    ),
                ],
                "invoice_plan_ids": [
                    (
                        0,
                        0,
                        {
                            "installment": 1,
                            "plan_date": "2026-02-23",
                            "invoice_type": "installment",
                            "percent": 50.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "installment": 2,
                            "plan_date": "2026-03-23",
                            "invoice_type": "installment",
                            "percent": 50.0,
                        },
                    ),
                ],
            }
        )

    def test_sale_order_report_render_smoke(self):
        report_model = self.env["ir.actions.report"].with_context(
            discard_logo_check=True
        )
        html, _ = report_model._render_qweb_html(
            "sale.action_report_saleorder", self.sale_order.ids
        )
        self.assertTrue(html)
