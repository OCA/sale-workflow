# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleLeadTime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        country_jp = cls.env.ref("base.jp")
        cls.country_us = cls.env.ref("base.us")
        state_tokyo = cls.env.ref("base.state_jp_jp-13")
        warehouse_obj = cls.env["stock.warehouse"]
        cls.warehouse_main = warehouse_obj.create({"name": "Main WH", "code": "MW"})
        cls.warehouse_2nd = warehouse_obj.create({"name": "2ndn WH", "code": "2W"})
        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "Cust A", "country_id": country_jp.id, "state_id": state_tokyo.id}
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {"name": "Cust B", "country_id": country_jp.id, "state_id": state_tokyo.id}
        )
        cls.partner_3 = cls.env["res.partner"].create(
            {"name": "Cust C", "country_id": cls.country_us.id}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product", "sale_delay": 10}
        )
        sale_order_model = cls.env["ir.model"].search(
            [("model", "=", "sale.order")], limit=1
        )
        # Prepare lead time profiles like the following:
        # +---------+-------+---------+-----------+------------------+
        # | Country | State | Partner | Warehouse | Lead Time (Days) |
        # +=========+=======+=========+===========+==================+
        # | Japan   | Tokyo | Cust A  |           |              3.0 |
        # +---------+-------+---------+-----------+------------------+
        # | Japan   | Tokyo |         | Main WH   |              5.0 |
        # +---------+-------+---------+-----------+------------------+
        # | Japan   | Tokyo |         | 2nd WH    |              7.0 |
        # +---------+-------+---------+-----------+------------------+
        # |         |       |         |           |             20.0 |
        # +---------+-------+---------+-----------+------------------+
        profile_obj = cls.env["lead.time.profile"]
        profile_obj.create(
            {
                "country_id": country_jp.id,
                "state_id": state_tokyo.id,
                "partner_id": cls.partner_1.id,
                "model_id": sale_order_model.id,
                "lead_time": 3.0,
            }
        )
        profile_obj.create(
            {
                "country_id": country_jp.id,
                "state_id": state_tokyo.id,
                "warehouse_id": cls.warehouse_main.id,
                "model_id": sale_order_model.id,
                "lead_time": 5.0,
            }
        )
        profile_obj.create(
            {
                "country_id": country_jp.id,
                "state_id": state_tokyo.id,
                "warehouse_id": cls.warehouse_2nd.id,
                "model_id": sale_order_model.id,
                "lead_time": 7.0,
            }
        )
        profile_obj.create({"model_id": sale_order_model.id, "lead_time": 20.0})

    def create_sale_order(self, partner, warehouse):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "warehouse_id": warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_sale_order_to_picking(self):
        company = self.env.company
        self.assertEqual(company.lead_time_profile_country_factor, 1.0)
        self.assertEqual(company.lead_time_profile_state_factor, 1.0)
        self.assertEqual(company.lead_time_profile_partner_factor, 1.0)
        self.assertEqual(company.lead_time_profile_warehouse_factor, 1.0)
        order = self.create_sale_order(self.partner_1, self.warehouse_main)
        # Profile with shorter lead time is picked in a tie-breaking situation
        self.assertEqual(order.delivery_lead_time, 3.0)
        # sale_delay of the product (10 days) + delivery_lead_time (3 days)
        self.assertEqual(order.order_line.customer_lead, 13.0)
        order.action_confirm()
        # Confirm that the delivery lead time is correctly accounted for in the
        # dates of picking
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date.date() + timedelta(days=3.0),
            picking.date_deadline.date(),
        )

    def test_profile_field_factors(self):
        company = self.env.company
        company.lead_time_profile_warehouse_factor = 2.0
        order = self.create_sale_order(self.partner_1, self.warehouse_main)
        self.assertEqual(order.delivery_lead_time, 5.0)

    def test_misc_order_patterns(self):
        order = self.create_sale_order(self.partner_2, self.warehouse_main)
        self.assertEqual(order.delivery_lead_time, 5.0)
        order.warehouse_id = self.warehouse_2nd
        self.assertEqual(order.delivery_lead_time, 7.0)
        order.partner_shipping_id = self.partner_3
        self.assertEqual(order.delivery_lead_time, 20.0)
