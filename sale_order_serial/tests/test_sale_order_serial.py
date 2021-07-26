# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSaleOrderSerial(common.TransactionCase):
    def test_sale_order_serial(self):
        partner_1 = self.env["res.partner"].create({"name": "Test partner1"})
        partner_2 = self.env["res.partner"].create(
            {
                "name": "Test partner2",
                "serial_sequence_id": self.env.ref("stock.sequence_production_lots").id,
            }
        )
        att = self.env.ref("product.product_attribute_value_1")
        att.serial_sequence_id = self.env.ref("stock.sequence_production_lots").id
        product1 = self.env["product.product"].create(
            {
                "name": "TestProduct",
                "tracking": "serial",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.env.ref(
                                "product.product_attribute_1"
                            ).id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    self.env.ref(
                                        "product.product_attribute_value_1"
                                    ).ids,
                                )
                            ],
                        },
                    )
                ],
            }
        )
        product2 = self.env["product.product"].create(
            {
                "name": "TestProduct",
                "tracking": "serial",
                "serial_sequence_id": self.env.ref("stock.sequence_production_lots").id,
            }
        )

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product1.id,
                            "serial_sequence_id": self.env.ref(
                                "stock.sequence_production_lots"
                            ).id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        self.assertFalse(sale_order.order_line[0].serial_list)
        sale_order.action_fill_serials()
        self.assertTrue(sale_order.order_line[0].serial_list)

        company1 = self.env["res.company"].create({"name": "Test company1"})
        production_lot_id = self.env["stock.production.lot"].create(
            {"product_id": product1.id, "company_id": company1.id}
        )

        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "partner_id": partner_1.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product1.id,
                                "serial_sequence_id": self.env.ref(
                                    "stock.sequence_production_lots"
                                ).id,
                                "product_uom_qty": 1,
                                "serial_list": production_lot_id.name,
                            },
                        )
                    ],
                }
            )

        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "partner_id": partner_1.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product1.id,
                                "product_uom_qty": 1,
                                "serial_list": "testserial",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "product_id": product1.id,
                                "product_uom_qty": 1,
                                "serial_list": "testserial",
                            },
                        ),
                    ],
                }
            )

        self.env["sale.order"].create(
            {
                "partner_id": partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product1.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "partner_id": partner_1.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product1.id,
                                "product_uom_qty": 1,
                                "serial_list": "testserial\ntest2",
                            },
                        )
                    ],
                }
            )

            self.env["sale.order"].create(
                {
                    "partner_id": partner_1.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product1.id,
                                "product_uom_qty": 2,
                                "serial_list": "testserial",
                            },
                        )
                    ],
                }
            )

        saleorder1 = self.env["sale.order"].create({"partner_id": partner_1.id})
        self.env["sale.order.line"].with_context(
            skip_existing_serials_check=1, skip_existing_soline_check=1
        ).create(
            {
                "product_id": product1.id,
                "serial_sequence_id": self.env.ref("stock.sequence_production_lots").id,
                "product_uom_qty": 1,
                "serial_list": "testserial",
                "order_id": saleorder1.id,
            }
        )

        sale_order2 = self.env["sale.order"].create({"partner_id": partner_1.id})
        product_tmplt_id = self.env["product.template"].create(
            {"name": "Test template"}
        )

        wiz = self.env["sale.order.line.from_stock"].create(
            {
                "sale_id": sale_order2.id,
                "product_tmpl_id": product_tmplt_id.id,
                "serial_list": production_lot_id.name,
                "value_ids": [
                    (6, 0, self.env.ref("product.product_attribute_value_1").ids)
                ],
            }
        )
        wiz.onchange_quant_ids()
        wiz.add()

        wiz2 = self.env["sale.order.line.from_stock"].create(
            {"sale_id": sale_order2.id, "serial_list": "t3\nt4"}
        )
        wiz2.onchange_quant_ids()
        wiz2.add()

        sale_order3 = self.env["sale.order"].create(
            {
                "partner_id": partner_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product2.id,
                            "product_uom_qty": 1,
                            "serial_list": "test1\ntest222",
                        },
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            sale_order3.action_fill_serials()

        sale_order4 = self.env["sale.order"].create(
            {
                "partner_id": partner_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product2.id,
                            "product_uom_qty": 2,
                            "serial_list": "test11",
                        },
                    )
                ],
            }
        )
        sale_order4.action_fill_serials()

        product3 = self.env["product.product"].create(
            {
                "name": "TestProduct3",
                "tracking": "serial",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.env.ref(
                                "product.product_attribute_3"
                            ).id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    self.env.ref(
                                        "product.product_attribute_value_5"
                                    ).ids,
                                )
                            ],
                        },
                    )
                ],
            }
        )
        self.env["sale.order"].create(
            {
                "partner_id": partner_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product3.id,
                            "product_uom_qty": 2,
                            "product_no_variant_attribute_value_ids": [
                                (
                                    6,
                                    0,
                                    self.env.ref(
                                        "product.product_attribute_value_5"
                                    ).ids,
                                )
                            ],
                        },
                    )
                ],
            }
        )
