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
        cls.env.company.sale_group_by_commitment_date = True
        sale_obj = cls.env["sale.order"]
        cls.move_ob = cls.env["stock.move"]
        cls.proc_group_obj = cls.env["procurement.group"]
        order_line = cls.env["sale.order.line"]
        Product = cls.env["product.product"]
        p1 = Product.create({"name": "p1", "type": "consu"}).id
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

        cls.sale3 = sale_obj.create({"partner_id": 1})
        cls.sale_line9 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale3.id,
                "commitment_date": cls.dt1,
            }
        )
        cls.sale_line10 = order_line.create(
            {
                "product_id": p1,
                "name": "cool product",
                "order_id": cls.sale3.id,
            }
        )

        cls.route = cls.env["stock.route"].create(
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
                "location_dest_id": sale1_cust_loc.id,
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
        group = self.proc_group_obj.search(
            [("name", "=", self.sale1.name + "/" + com_date)]
        )
        self.assertEqual(len(group), 1)
        moves = self.move_ob.search([("group_id", "=", group.id)])
        self.assertEqual(len(moves), 2)

        com_date2 = fields.Date.to_string(self.dt2)
        group = self.proc_group_obj.search(
            [("name", "=", self.sale1.name + "/" + com_date2)]
        )
        self.assertEqual(len(group), 1)
        moves = self.move_ob.search([("group_id", "=", group.id)])
        self.assertEqual(len(moves), 2)

        self.sale2.action_confirm()
        group = self.proc_group_obj.search(
            [("name", "=", self.sale2.name + "/" + com_date)]
        )
        self.assertEqual(len(group), 1)
        moves = self.move_ob.search([("group_id", "=", group.id)])
        self.assertEqual(len(moves), 4)

    def test_line_without_commitment_date(self):
        """A line without commitment date stays in the order's own group,
        apart from the lines that have one"""
        self.sale3.action_confirm()
        undated_group = self.sale_line10.move_ids.group_id
        self.assertEqual(undated_group.name, self.sale3.name)
        com_date = fields.Date.to_string(self.dt1)
        dated_group = self.sale_line9.move_ids.group_id
        self.assertEqual(dated_group.name, self.sale3.name + "/" + com_date)

    def test_move_date_from_commitment_date(self):
        """The move is planned at the commitment date minus the security
        lead time, and its deadline is the commitment date"""
        self.sale1.company_id.security_lead = 1
        self.sale1.action_confirm()
        commitment_date = self.sale_line1.commitment_date.replace(microsecond=0)
        move = self.sale_line1.move_ids
        self.assertEqual(
            move.date.replace(microsecond=0),
            commitment_date - datetime.timedelta(days=1),
        )
        self.assertEqual(move.date_deadline.replace(microsecond=0), commitment_date)
