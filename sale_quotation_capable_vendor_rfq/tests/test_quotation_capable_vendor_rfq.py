# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("test11")
class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.vendor_1 = cls.env.ref("base.res_partner_2")
        cls.vendor_2 = cls.env.ref("base.res_partner_3")
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_2 = cls.env.ref("product.product_product_2")
        cls.sale_order = cls.env["sale.order"]
        cls.sale_order_line = cls.env["sale.order.line"]
        cls.product_1.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_1.id,
                            "price": 100,
                            "min_qty": 2,
                            "delay": 2,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_1.id,
                            "price": 90,
                            "min_qty": 4,
                            "delay": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_2.id,
                            "price": 110,
                            "min_qty": 5,
                            "delay": 1,
                        },
                    ),
                ]
            }
        )
        cls.product_2.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_2.id,
                            "price": 100,
                            "min_qty": 2,
                            "delay": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_2.id,
                            "price": 90,
                            "min_qty": 4,
                            "delay": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_1.id,
                            "price": 110,
                            "min_qty": 5,
                            "delay": 1,
                        },
                    ),
                ]
            }
        )

    def test_create_rfq_with_sale_order1(self):
        """Test creating RFQ with sale order"""

        # Create sale order
        sale_order = self.sale_order.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product_1.uom_id.id,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product_2.uom_id.id,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        sale_order._create_rfq()
        # Check RFQ
        self.assertEqual(sale_order.partner_id, self.partner)
        self.assertEqual(len(sale_order.order_line), 2)
        self.assertEqual(sale_order.rfq_count, 2)

        # Check RFQ
        purchase_order_1 = sale_order.rfq_ids.filtered(
            lambda p: p.partner_id == self.vendor_1
        )
        self.assertEqual(len(purchase_order_1), 1)
        self.assertEqual(purchase_order_1.partner_id.id, self.vendor_1.id)
        self.assertEqual(len(purchase_order_1.order_line), 1)
        purchase_order_1_line_1 = purchase_order_1.order_line.filtered(
            lambda l: l.product_id == self.product_1
        )
        self.assertEqual(purchase_order_1_line_1.price_unit, 100)

        purchase_order_1_line_2 = purchase_order_1.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        self.assertEqual(len(purchase_order_1_line_2), 0)

        purchase_order_2 = sale_order.rfq_ids.filtered(
            lambda p: p.partner_id == self.vendor_2
        )
        self.assertEqual(len(purchase_order_2), 1)
        self.assertEqual(purchase_order_2.partner_id.id, self.vendor_2.id)
        self.assertEqual(len(purchase_order_2.order_line), 1)

        purchase_order_2_line_1 = purchase_order_2.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        self.assertEqual(purchase_order_2_line_1.price_unit, 100)

        purchase_order_2_line_2 = purchase_order_2.order_line.filtered(
            lambda l: l.product_id == self.product_1
        )
        self.assertEqual(len(purchase_order_2_line_2), 0)

    def test_create_rfq_with_sale_order2(self):
        """Test creating RFQ with sale order"""

        # Create sale order
        sale_order = self.sale_order.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_1.uom_id.id,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_2.uom_id.id,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        sale_order._create_rfq()
        # Check RFQ
        self.assertEqual(sale_order.partner_id, self.partner)
        self.assertEqual(len(sale_order.order_line), 2)
        self.assertEqual(sale_order.rfq_count, 2)

        # Check RFQ
        purchase_order_1 = sale_order.rfq_ids.filtered(
            lambda p: p.partner_id == self.vendor_1
        )
        self.assertEqual(len(purchase_order_1), 1)
        self.assertEqual(purchase_order_1.partner_id.id, self.vendor_1.id)
        self.assertEqual(len(purchase_order_1.order_line), 2)
        purchase_order_1_line_1 = purchase_order_1.order_line.filtered(
            lambda l: l.product_id == self.product_1
        )
        self.assertEqual(purchase_order_1_line_1.price_unit, 90)

        purchase_order_1_line_2 = purchase_order_1.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        self.assertEqual(purchase_order_1_line_2.price_unit, 110)

        purchase_order_2 = sale_order.rfq_ids.filtered(
            lambda p: p.partner_id == self.vendor_2
        )
        self.assertEqual(len(purchase_order_2), 1)
        self.assertEqual(purchase_order_2.partner_id.id, self.vendor_2.id)
        self.assertEqual(len(purchase_order_2.order_line), 2)

        purchase_order_2_line_1 = purchase_order_2.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        self.assertEqual(purchase_order_2_line_1.price_unit, 90)

        purchase_order_2_line_2 = purchase_order_2.order_line.filtered(
            lambda l: l.product_id == self.product_1
        )
        self.assertEqual(purchase_order_2_line_2.price_unit, 110)

    def test_product_product(self):
        suplierinfos_1 = self.product_1._get_matching_vendor_pricelists(1)
        self.assertEqual(len(suplierinfos_1), 0)
        suplierinfos_2 = self.product_1._get_matching_vendor_pricelists(2)
        self.assertEqual(len(suplierinfos_2), 1)
        self.assertEqual(suplierinfos_2[0].partner_id, self.vendor_1)
        self.assertEqual(suplierinfos_2[0].price, 100)
        suplierinfos_3 = self.product_1._get_matching_vendor_pricelists(10)
        self.assertEqual(len(suplierinfos_3), 2)
        suplierinfos_3_vendor_1 = suplierinfos_3.filtered(
            lambda s: s.partner_id == self.vendor_1
        )
        self.assertEqual(len(suplierinfos_3_vendor_1), 1)
        self.assertEqual(suplierinfos_3_vendor_1.price, 90)
        suplierinfos_3_vendor_2 = suplierinfos_3.filtered(
            lambda s: s.partner_id == self.vendor_2
        )
        self.assertEqual(len(suplierinfos_3_vendor_2), 1)
        self.assertEqual(suplierinfos_3_vendor_2.price, 110)
        suplierinfos_4 = self.product_1._get_matching_vendor_pricelists(10, 2)
        self.assertEqual(len(suplierinfos_4), 1)
        self.assertEqual(suplierinfos_4[0].partner_id, self.vendor_1)
        self.assertEqual(suplierinfos_4[0].price, 100)
