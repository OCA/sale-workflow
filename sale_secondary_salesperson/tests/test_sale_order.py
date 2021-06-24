# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from psycopg2 import IntegrityError

from odoo.tests import Form, common
from odoo.tools import mute_logger


class TestSaleOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.partner = cls.env.ref("base.res_partner_12")

    def test_sale_with_equal_secondary_user_id(self):
        order = Form(self.env["sale.order"])
        order.partner_id = self.partner
        order.user_id = self.user_admin
        order.secondary_user_id = self.user_admin
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            order.save()
