# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
<<<<<<< HEAD
        cls.product_uom_kg = cls.env.ref("product.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("product.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("product.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-700",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [
                ("product_tmpl_id", "=", cls.product.product_tmpl_id.id),
            ]
        )
        cls.product_uom_kg = cls.env.ref('uom.product_uom_kgm')
        cls.product_uom_gram = cls.env.ref('uom.product_uom_gram')
        cls.product_uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'uom_id': cls.product_uom_kg.id,
            'uom_po_id': cls.product_uom_kg.id,
            'secondary_uom_ids': [
                (0, 0, {
                    'name': 'unit-700',
                    'uom_id': cls.product_uom_unit.id,
                    'factor': 0.7,
                })],
        })
        cls.secondary_unit = cls.env['product.secondary.unit'].search([
            ('product_tmpl_id', '=', cls.product.product_tmpl_id.id),
        ])
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        cls.product_uom_kg = cls.env.ref('uom.product_uom_kgm')
        cls.product_uom_gram = cls.env.ref('uom.product_uom_gram')
        cls.product_uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'uom_id': cls.product_uom_kg.id,
            'uom_po_id': cls.product_uom_kg.id,
            'secondary_uom_ids': [
                (0, 0, {
                    'name': 'unit-700',
                    'uom_id': cls.product_uom_unit.id,
                    'factor': 0.7,
                })],
        })
        cls.secondary_unit = cls.env['product.secondary.unit'].search([
            ('product_tmpl_id', '=', cls.product.product_tmpl_id.id),
        ])
=======
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-500",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    )
                ],
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
<<<<<<< HEAD
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "test - partner",
            }
        )
        so = cls.env["sale.order"].new(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        cls.partner = cls.env['res.partner'].create({
            'name': 'test - partner',
        })
        so = cls.env['sale.order'].new({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 1000.00,
            })],
            'pricelist_id': cls.env.ref('product.list0').id,
        })
=======
||||||| parent of d16be0e27 ([FIX] code refactor)
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
=======
        cls.product.secondary_uom_ids = cls.secondary_unit.id
>>>>>>> d16be0e27 ([FIX] code refactor)
||||||| parent of e596a34a8 (code refactor update)
        cls.product.secondary_uom_ids = cls.secondary_unit.id
=======
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
>>>>>>> e596a34a8 (code refactor update)
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        so = cls.env["sale.order"].new(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        so.onchange_partner_id()
        cls.order = cls.env["sale.order"].create(so._convert_to_write(so._cache))

    def test_onchange_secondary_uom(self):
<<<<<<< HEAD
        self.order.order_line.write(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "secondary_uom_qty": 5,
            }
        )
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        self.order.order_line.write({
            'secondary_uom_id': self.secondary_unit.id,
            'secondary_uom_qty': 5,
        })
=======
        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "secondary_uom_qty": 5}
        )
<<<<<<< HEAD
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        self.order.order_line.onchange_secondary_uom()
||||||| parent of e596a34a8 (code refactor update)
        self.order.order_line.onchange_secondary_uom()
=======
        self.order.order_line._compute_product_uom_qty()
<<<<<<< HEAD
>>>>>>> e596a34a8 (code refactor update)
        self.assertEqual(self.order.order_line.product_uom_qty, 3.5)
||||||| parent of ba4f2a6c3 (add secondary price unit)
        self.assertEqual(self.order.order_line.product_uom_qty, 3.5)
=======
        self.assertEqual(self.order.order_line.product_uom_qty, 2.5)
>>>>>>> ba4f2a6c3 (add secondary price unit)

    def test_onchange_secondary_unit_product_uom_qty(self):
<<<<<<< HEAD
        self.order.order_line.update(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "product_uom_qty": 3.5,
            }
        )
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        self.order.order_line.update({
            'secondary_uom_id': self.secondary_unit.id,
            'product_uom_qty': 3.5,
        })
=======
        self.order.order_line.update(
            {"secondary_uom_id": self.secondary_unit.id, "product_uom_qty": 3.5}
        )
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        self.order.order_line.onchange_secondary_unit_product_uom_qty()
||||||| parent of e596a34a8 (code refactor update)
        self.order.order_line.onchange_secondary_unit_product_uom_qty()
=======
>>>>>>> e596a34a8 (code refactor update)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 5.0)
||||||| parent of ba4f2a6c3 (add secondary price unit)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 5.0)
=======
        self.assertEqual(self.order.order_line.secondary_uom_qty, 7.0)
>>>>>>> ba4f2a6c3 (add secondary price unit)

    def test_default_secondary_unit(self):
        self.order.order_line.onchange_secondary_unit_product_id()
        self.assertEqual(self.order.order_line.secondary_uom_id, self.secondary_unit)
        self.order.order_line.product_id_change()
        self.assertEqual(self.order.order_line.secondary_uom_id, self.secondary_unit)

    def test_onchange_order_product_uom(self):
        self.order.order_line.update(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "product_uom": self.product_uom_gram.id,
                "product_uom_qty": 3500.00,
            }
        )
        self.assertEqual(self.order.order_line.secondary_uom_qty, 7.0)

    def test_independent_type(self):
        # dependent type is already tested as dependency_type by default
        self.order.order_line.secondary_uom_id = self.secondary_unit.id
        self.order.order_line.secondary_uom_id.write({"dependency_type": "independent"})

        # Remember previous UoM quantity for avoiding interactions with other modules
        previous_uom_qty = self.order.order_line.product_uom_qty
        self.order.order_line.write({"secondary_uom_qty": 2})
        self.assertEqual(self.order.order_line.product_uom_qty, previous_uom_qty)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 2)

        self.order.order_line.write({"product_uom_qty": 17})
        self.assertEqual(self.order.order_line.secondary_uom_qty, 2)
        self.assertEqual(self.order.order_line.product_uom_qty, 17)

    def test_secondary_uom_unit_price(self):
        self.assertEqual(self.order.order_line.secondary_uom_unit_price, 0)
        self.order.order_line.update(
            {"secondary_uom_id": self.secondary_unit.id, "product_uom_qty": 2}
        )

        self.assertEqual(self.order.order_line.secondary_uom_qty, 4)
        self.assertEqual(self.order.order_line.secondary_uom_unit_price, 500)

        self.order.order_line.write({"product_uom_qty": 8})
        self.assertEqual(self.order.order_line.secondary_uom_qty, 16)
        self.assertEqual(self.order.order_line.secondary_uom_unit_price, 500)
        self.assertEqual(self.order.order_line.price_subtotal, 8000)
