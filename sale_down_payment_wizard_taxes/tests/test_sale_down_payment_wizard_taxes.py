# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests.common import SavepointCase


class TestSaleOrderLinePriceUnitFixed(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.PriceList = cls.env["product.pricelist"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.partner = cls.Partner.create({"name": "Customer"})
        cls.product1 = cls.Product.create({"name": "Test Product 1", "list_price": 10})
        cls.tax15 = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 15.0,
            }
        )

        cls.sale_order = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "name": "line 1",
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    ),
                ],
            }
        )

        # Context
        cls.context = {
            "active_model": "sale.order",
            "active_ids": [cls.sale_order.id],
            "active_id": cls.sale_order.id,
        }

    def test_downpayment(self):
        """Test downpayment and ensures
        that the tax is the same on the invoice and the sale order"""
        so = self.sale_order
        # Confirm the SO
        so.action_confirm()
        # Let's do an invoice for a deposit of 100 and 15% tax
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create(
                {
                    "advance_payment_method": "fixed",
                    "fixed_amount": 100,
                    "deposit_taxes_id": self.tax15,
                }
            )
        )
        payment.create_invoices()

        self.assertEqual(len(so.invoice_ids), 1, "Invoice should be created for the SO")
        downpayment_line = so.order_line.filtered(lambda l: l.is_downpayment)
        self.assertEqual(
            len(downpayment_line), 1, "SO line downpayment should be created on SO"
        )

        inv_line = first(first(so.invoice_ids).invoice_line_ids)
        self.assertEqual(downpayment_line.tax_id, first(inv_line.tax_ids))
        self.assertEqual(downpayment_line.tax_id, self.tax15)
        self.assertEqual(first(inv_line.tax_ids), self.tax15)
