from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestSaleReport(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_order_types = cls.env["sale.order.type"].create(
            [
                {
                    "name": "Normal Order",
                },
                {
                    "name": "Special Order",
                },
            ]
        )

        # Create the SO with one order line
        cls.sale_order = (
            cls.env["sale.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": cls.partner_a.id,
                    "partner_invoice_id": cls.partner_a.id,
                    "partner_shipping_id": cls.partner_a.id,
                    "type_id": cls.sale_order_types[0].id,  # Normal Order
                }
            )
        )
        SaleOrderLine = cls.env["sale.order.line"].with_context(tracking_disable=True)
        cls.sol_prod_order = SaleOrderLine.create(
            {
                "name": cls.company_data["product_order_no"].name,
                "product_id": cls.company_data["product_order_no"].id,
                "product_uom_qty": 5,
                "product_uom_id": cls.company_data["product_order_no"].uom_id.id,
                "price_unit": cls.company_data["product_order_no"].list_price,
                "order_id": cls.sale_order.id,
                "tax_ids": False,
            }
        )

    def test_sale_report_sale_order_type(self):
        self.env["sale.report"]._read_group(
            domain=[],
            groupby=["type_id"],
            aggregates=["product_id:recordset", "product_uom_qty:sum"],
        )
