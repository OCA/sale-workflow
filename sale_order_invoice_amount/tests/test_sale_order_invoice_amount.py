# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common


class TestSaleOrderInvoiceAmount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Wood Corner"})
        cls.res_partner_address_1 = cls.env["res.partner"].create(
            {"name": "Willie Burke", "parent_id": cls.res_partner_1.id}
        )
        cls.res_partner_2 = cls.env["res.partner"].create({"name": "Partner 12"})
        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Desk Combination", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Conference Chair", "type": "product"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Repair Services", "type": "service"}
        )
        # Location
        cls.stock_warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location_14 = cls.env["stock.location"].create(
            {"name": "Shelf 2", "location_id": cls.stock_warehouse.lot_stock_id.id}
        )
        # Replenish products
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.stock_location_14, 10
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.stock_location_14, 10
        )
        # Sale Order
        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax 15", "type_tax_use": "sale", "amount": 21}
        )
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        cls.order_line_1 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_2 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 4.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_3 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 5.0,
                "tax_id": cls.tax,
            }
        )

    def test_sale_order_invoiced_amount(self):
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            0.0,
            "Invoiced Amount should be 0.0",
        )
        context_payment = {
            "active_ids": [self.sale_order_1.id],
            "active_id": self.sale_order_1.id,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(**context_payment)
            .create({"advance_payment_method": "fixed", "fixed_amount": 100})
        )

        payment.create_invoices()
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            100.0,
            "Invoiced Amount should be 100",
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            263.0,
            "Uninvoiced Amount should be 263",
        )

        self.sale_order_1.action_confirm()
        self.sale_order_1._create_invoices(final=True)
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            363.0,
            "Invoiced Amount should be calculated",
        )
