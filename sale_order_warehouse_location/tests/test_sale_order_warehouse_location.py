# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderWarehouseLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.country_spain_id = cls.env.ref("base.es").id
        cls.state_spain_id = cls.env.ref("base.state_es_v").id
        cls.country_uk_id = cls.env.ref("base.uk").id
        cls.state_uk_id = cls.env.ref("base.state_uk34").id
        cls.warehouse_es = cls.env["stock.warehouse"].create(
            {
                "name": "WH-1",
                "code": "WH-1",
                "sale_country_ids": [cls.country_spain_id],
                "sale_state_ids": [cls.state_spain_id],
            }
        )
        cls.warehouse_uk = cls.env["stock.warehouse"].create(
            {
                "name": "WH-2",
                "code": "WH-2",
                "sale_country_ids": [cls.country_uk_id],
                "sale_state_ids": [cls.state_uk_id],
            }
        )
        cls.partner_es = cls.env["res.partner"].create(
            {
                "name": "Partner Spain",
                "country_id": cls.country_spain_id,
                "state_id": cls.state_spain_id,
            }
        )
        cls.partner_uk = cls.env["res.partner"].create(
            {
                "name": "Partner UK",
                "country_id": cls.country_uk_id,
                "state_id": cls.state_uk_id,
            }
        )
        cls.partner_be = cls.env["res.partner"].create(
            {
                "name": "Partner UK",
                "country_id": cls.env.ref("base.be").id,
            }
        )

    def test_so_warehouse_location_country_state(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_es.id,
            }
        )
        self.assertEqual(order.warehouse_id, self.warehouse_es)
        order.write({"partner_id": self.partner_uk.id})
        self.assertEqual(order.warehouse_id, self.warehouse_uk)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_be.id,
            }
        )
        warehouse = order.user_id._get_default_warehouse_id()
        self.assertEqual(order.warehouse_id, warehouse)

    def test_so_warehouse_location_only_country(self):
        self.warehouse_es.write({"sale_state_ids": []})
        self.warehouse_uk.write({"sale_state_ids": []})
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_es.id,
            }
        )
        self.assertEqual(order.warehouse_id, self.warehouse_es)
        order.write({"partner_id": self.partner_uk.id})
        self.assertEqual(order.warehouse_id, self.warehouse_uk)

    def test_warehouse_state_compute(self):
        self.warehouse_es.write(
            {
                "sale_country_ids": [(4, self.country_uk_id)],
                "sale_state_ids": [(4, self.state_uk_id)],
            }
        )
        self.assertTrue(self.country_spain_id in self.warehouse_es.sale_country_ids.ids)
        self.assertTrue(self.country_uk_id in self.warehouse_es.sale_country_ids.ids)
        self.assertEqual(len(self.warehouse_es.sale_country_ids), 2)
        self.assertTrue(self.state_spain_id in self.warehouse_es.sale_state_ids.ids)
        self.assertTrue(self.state_uk_id in self.warehouse_es.sale_state_ids.ids)
        self.assertEqual(len(self.warehouse_es.sale_state_ids), 2)
        self.warehouse_es.write(
            {
                "sale_country_ids": [(3, self.country_spain_id)],
            }
        )
        self.assertFalse(
            self.country_spain_id in self.warehouse_es.sale_country_ids.ids
        )
        self.assertTrue(self.country_uk_id in self.warehouse_es.sale_country_ids.ids)
        self.assertEqual(len(self.warehouse_es.sale_country_ids), 1)
        self.assertFalse(self.state_spain_id in self.warehouse_es.sale_state_ids.ids)
        self.assertTrue(self.state_uk_id in self.warehouse_es.sale_state_ids.ids)
        self.assertEqual(len(self.warehouse_es.sale_state_ids), 1)
