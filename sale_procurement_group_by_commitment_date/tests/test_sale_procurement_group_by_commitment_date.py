# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleMultiPickingByCommitmentDate(TransactionCase):
    """Check the _get_shipped method of Sale Order."""

    @classmethod
    def setUpClass(cls):
        """Setup a Sale Order with 4 lines.
        And prepare procurements
        """
        super().setUpClass()
        sale_obj = cls.env["sale.order"]
        cls.move_ob = cls.env["stock.move"]
        cls.proc_group_obj = cls.env["procurement.group"]
        order_line = cls.env["sale.order.line"]
        Product = cls.env["product.product"]
        p1 = Product.create({"name": "p1", "type": "product"}).id
        today = datetime.datetime.now()
        cls.dt1 = today
        cls.dt2 = today + datetime.timedelta(days=1)

        cls.sale1 = sale_obj.create({"partner_id": 1})
        cls.sale_line1 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale1.id,
                "commitment_date": cls.dt1,
            }
        )
        cls.sale_line2 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale1.id,
                "commitment_date": cls.dt2,
            }
        )
        cls.sale_line3 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale1.id,
                "commitment_date": cls.dt1,
            }
        )
        cls.sale_line4 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale1.id,
                "commitment_date": cls.dt2,
            }
        )

        cls.sale2 = sale_obj.create({"partner_id": 1})
        cls.sale_line5 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale2.id,
                "commitment_date": cls.dt1,
            }
        )
        cls.sale_line6 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale2.id,
                "commitment_date": cls.dt1,
            }
        )
        cls.sale_line7 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale2.id,
                "commitment_date": cls.dt1,
            }
        )
        cls.sale_line8 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale2.id,
                "commitment_date": cls.dt1,
            }
        )

        cls.route = cls.env["stock.location.route"].create(
            {
                "sale_selectable": True,
                "name": "test_route",
                "warehouse_ids": [(4, cls.sale1.warehouse_id.id)],
            }
        )
        sale1_cust_loc = cls.sale1.partner_shipping_id.property_stock_customer
        sale1_wh = cls.sale1.warehouse_id
        cls.env["stock.rule"].create(
            {
                "name": "test_rule",
                "action": "pull",
                "location_id": sale1_cust_loc.id,
                "location_src_id": sale1_wh.view_location_id.id,
                "route_id": cls.route.id,
                "picking_type_id": sale1_wh.out_type_id.id,
                "warehouse_id": sale1_wh.id,
            }
        )

    def test_number_of_groups(self):
        """True when the number of groups created matches the
        result of multiply the different warehouses with the different
        commitment dates"""
        self.sale1.action_confirm()
        com_date = fields.Date.to_string(self.dt1)
        g_name = self.sale1.name + "/" + com_date
        groups = self.proc_group_obj.search([("name", "=", g_name)])

        for group in groups:
            if group.name == g_name:
                procurements = self.move_ob.search([("group_id", "=", group.id)])
                self.assertEqual(len(procurements), 2)
        self.assertEqual(len(groups), 1)

        com_date2 = fields.Date.to_string(self.dt2)
        g_name = self.sale1.name + "/" + com_date2
        groups = self.proc_group_obj.search([("name", "=", g_name)])

        for group in groups:
            if group.name == g_name:
                procurements = self.move_ob.search([("group_id", "=", group.id)])
                self.assertEqual(len(procurements), 2)
        self.assertEqual(len(groups), 1)

        self.sale2.action_confirm()
        g_name = self.sale2.name + "/" + com_date
        groups = self.proc_group_obj.search([("name", "=", g_name)])
        for group in groups:
            if group.name == g_name:
                procurements = self.move_ob.search([("group_id", "=", group.id)])
                self.assertEqual(len(procurements), 4)
        self.assertEqual(len(groups), 1)
