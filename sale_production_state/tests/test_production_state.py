# Copyright 2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestSaleProductionState(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        route_manufacture_1 = cls.env.ref("mrp.route_warehouse0_manufacture")
        route_manufacture_2 = cls.env.ref("stock.route_warehouse0_mto")
        route_manufacture_2.active = True
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test sale production state product 1",
                "type": "product",
                "route_ids": [
                    (4, route_manufacture_1.id),
                    (4, route_manufacture_2.id),
                ],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test sale production state product",
                "type": "product",
            }
        )
        cls.bom_1 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_1.product_tmpl_id.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom_1.id, "product_id": cls.product.id, "product_qty": 1}
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test sale production state product 2",
                "type": "product",
                "route_ids": [
                    (4, route_manufacture_1.id),
                    (4, route_manufacture_2.id),
                ],
            }
        )
        cls.bom_2 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom_2.id, "product_id": cls.product.id, "product_qty": 1}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test client"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "client_order_ref": "SO1",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 1,
                            "price_unit": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 1,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )

    def test_no_production(self):
        self.assertEqual(self.order.order_line[0].production_state, "no")
        self.assertEqual(self.order.production_state, "no")

    def test_unprocessed_production(self):
        self.order.action_confirm()
        self.assertEqual(self.order.order_line[0].production_state, "unprocessed")
        self.assertEqual(self.order.production_state, "unprocessed")
        self.assertTrue(self.order.order_line[0].production_ids)

    def test_partially(self):
        self.order.action_confirm()
        mrp = self.order.order_line[0].production_ids
        mrp.action_confirm()
        mo_form = Form(mrp)
        mo_form.qty_producing = 1
        mrp = mo_form.save()
        mrp.button_mark_done()
        self.assertEqual(self.order.order_line[0].production_state, "done")
        self.assertEqual(self.order.production_state, "partially")

    def test_production_done(self):
        self.order.action_confirm()
        for line in self.order.order_line:
            mrp = line.production_ids
            mrp.action_confirm()
            mo_form = Form(mrp)
            mo_form.qty_producing = 1
            mrp = mo_form.save()
            mrp.button_mark_done()
        self.assertEqual(self.order.production_state, "done")
