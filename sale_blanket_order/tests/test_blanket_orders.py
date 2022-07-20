# Copyright (C) 2018 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestSaleBlanketOrders(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.blanket_order_obj = self.env["sale.blanket.order"]
        self.blanket_order_line_obj = self.env["sale.blanket.order.line"]
        self.blanket_order_wiz_obj = self.env["sale.blanket.order.wizard"]
        self.so_obj = self.env["sale.order"]

        self.payment_term = self.env.ref("account.account_payment_term_immediate")
        self.sale_pricelist = self.env["product.pricelist"].create(
            {"name": "Test Pricelist", "currency_id": self.env.ref("base.USD").id}
        )

        # UoM
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")
        self.uom_dozen = self.env["uom.uom"].create(
            {
                "name": "Test-DozenA",
                "category_id": self.categ_unit.id,
                "factor_inv": 12,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "TEST CUSTOMER",
                "property_product_pricelist": self.sale_pricelist.id,
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Demo",
                "categ_id": self.env.ref("product.product_category_1").id,
                "standard_price": 35.0,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL01",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Demo 2",
                "categ_id": self.env.ref("product.product_category_1").id,
                "standard_price": 50.0,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL02",
            }
        )

        self.yesterday = date.today() - timedelta(days=1)
        self.tomorrow = date.today() + timedelta(days=1)

    def test_01_create_blanket_order(self):
        """We create a blanket order and check constrains to confirm BO"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.yesterday),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 0.0,  # will be updated later
                        },
                    )
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.line_ids[0].sudo().onchange_product()
        blanket_order.line_ids[0].sudo()._get_display_price(self.product)

        self.assertEqual(blanket_order.state, "draft")

        # date in the past
        with self.assertRaises(UserError):
            blanket_order.sudo().action_confirm()

        blanket_order.validity_date = fields.Date.to_string(self.tomorrow)
        blanket_order.sudo().action_confirm()
        self.assertEqual(blanket_order.state, "open")

        blanket_order.sudo().action_cancel()
        self.assertEqual(blanket_order.state, "expired")

        blanket_order.sudo().set_to_draft()
        self.assertEqual(blanket_order.state, "draft")

        blanket_order.sudo().action_confirm()

    def test_02_create_sale_orders_from_blanket_order(self):
        """We create a blanket order and create two sale orders"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 30.0,
                        },
                    )
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.sudo().action_confirm()

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="sale.blanket.order"
        ).create({})
        wizard1.line_ids[0].write({"qty": 10.0})
        wizard1.sudo().create_sale_order()

        wizard2 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="sale.blanket.order"
        ).create({})
        wizard2.line_ids[0].write({"qty": 10.0})
        wizard2.sudo().create_sale_order()

        self.assertEqual(blanket_order.state, "done")

        self.assertEqual(blanket_order.sale_count, 2)

        view_action = blanket_order.action_view_sale_orders()
        domain_ids = view_action["domain"][0][2]
        self.assertEqual(len(domain_ids), 2)

        sos = self.so_obj.browse(domain_ids)
        for so in sos:
            self.assertEqual(so.origin, blanket_order.name)

    def test_03_create_sale_orders_from_blanket_order_line(self):
        """We create a blanket order and create two sale orders
        from the blanket order lines"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 30.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom": self.product2.uom_id.id,
                            "original_uom_qty": 50.0,
                            "price_unit": 60.0,
                        },
                    ),
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.sudo().action_confirm()
        bo_lines = blanket_order.line_ids
        self.assertEqual(len(bo_lines), 2)

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_ids=[bo_lines[0].id, bo_lines[1].id]
        ).create({})
        self.assertEqual(len(wizard1.line_ids), 2)
        wizard1.line_ids[0].write({"qty": 10.0})
        wizard1.line_ids[1].write({"qty": 20.0})
        wizard1.sudo().create_sale_order()

        self.assertEqual(bo_lines[0].remaining_uom_qty, 10.0)
        self.assertEqual(bo_lines[1].remaining_uom_qty, 30.0)

    def test_04_create_sale_order_add_blanket_order_line(self):
        """We create a blanket order and the separately we create
        a sale order and see if blanket order lines have been
        correctly assigned"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "currency_id": self.sale_pricelist.currency_id.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 30.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom": self.product2.uom_id.id,
                            "original_uom_qty": 50.0,
                            "price_unit": 60.0,
                        },
                    ),
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.sudo().action_confirm()

        bo_lines = blanket_order.line_ids

        sale_order = self.so_obj.create(
            {
                "partner_id": self.partner.id,
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 30.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom": self.product2.uom_id.id,
                            "product_uom_qty": 50.0,
                            "price_unit": 60.0,
                        },
                    ),
                ],
            }
        )
        sale_order.order_line[0].onchange_product_id()
        self.assertEqual(bo_lines[0].remaining_uom_qty, 10.0)

    def test_05_create_sale_order_blanket_order_with_different_uom(self):
        """We create a blanket order and the separately we create
        a sale order with different uom and see if blanket order
        lines have been correctly assigned"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.uom_dozen.id,
                            "original_uom_qty": 2.0,
                            "price_unit": 240.0,
                        },
                    )
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.sudo().action_confirm()

        sale_order = self.so_obj.create(
            {
                "partner_id": self.partner.id,
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 12.0,
                            "price_unit": 30.0,
                        },
                    )
                ],
            }
        )
        sale_order.order_line[0].onchange_product_id()
        sale_order.order_line[0].onchange_blanket_order_line()
        self.assertEqual(blanket_order.line_ids[0].remaining_qty, 12.0)
        self.assertEqual(sale_order.order_line[0].price_unit, 20.0)

    def test_06_create_sale_orders_from_blanket_order(self):
        """We create a blanket order and create three sale orders
        where the first two consume the first blanket order line
        """
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 30.0,
                            "price_unit": 30.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom": self.product2.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 60.0,
                        },
                    ),
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.sudo().action_confirm()

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="sale.blanket.order"
        ).create({})
        wizard1.line_ids.filtered(lambda l: l.product_id == self.product).write(
            {"qty": 10.0}
        )
        wizard1.line_ids.filtered(lambda l: l.product_id == self.product2).write(
            {"qty": 10.0}
        )
        wizard1.sudo().create_sale_order()

        wizard2 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="sale.blanket.order"
        ).create({})
        wizard2.line_ids.filtered(lambda l: l.product_id == self.product).write(
            {"qty": 20.0}
        )
        wizard2.line_ids.filtered(lambda l: l.product_id == self.product2).write(
            {"qty": 0}
        )
        wizard2.sudo().create_sale_order()

        wizard3 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="sale.blanket.order"
        ).create({})
        wizard3.line_ids.filtered(lambda l: l.product_id == self.product2).write(
            {"qty": 10.0}
        )
        wizard3.sudo().create_sale_order()

        self.assertEqual(blanket_order.state, "done")

        self.assertEqual(blanket_order.sale_count, 3)

        view_action = blanket_order.action_view_sale_orders()
        domain_ids = view_action["domain"][0][2]
        self.assertEqual(len(domain_ids), 3)
