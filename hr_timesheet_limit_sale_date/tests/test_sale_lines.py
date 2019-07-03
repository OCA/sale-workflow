# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import exceptions

from .common import TestCommonMixin


class TestSale(TestCommonMixin):
    def test_domain_default(self):
        domain = self.so_line._analytic_compute_delivered_quantity_domain()
        found = self.aal_model.search(domain)
        self.assertEqual(
            sorted(found.mapped('date')),
            sorted(('2019-05-08', '2019-05-09', '2019-05-10')),
        )

    def test_domain_timesheet_limit_date(self):
        domain = self.so_line.with_context(
            timesheet_limit_date='2019-05-09'
        )._analytic_compute_delivered_quantity_domain()
        found = self.aal_model.search(domain)
        self.assertEqual(
            sorted(found.mapped('date')), sorted(('2019-05-08', '2019-05-09'))
        )

    def test_delivered_limited(self):
        # while lines not validated no lines
        self.sale_order.timesheet_limit_date = '2019-05-09'
        self.assertFalse(self.so_line.qty_delivered)
        self.sale_order.timesheet_limit_date = '2019-05-09'
        self.assertEqual(self.so_line.qty_delivered, 2)
        self.sale_order.timesheet_limit_date = '2019-05-08'
        self.assertEqual(self.so_line.qty_delivered, 1)
        self.sale_order.timesheet_limit_date = '2019-05-07'
        self.assertEqual(self.so_line.qty_delivered, 0)
        # restored
        self.sale_order.timesheet_limit_date = False
        self.assertEqual(self.so_line.qty_delivered, 3)

    def test_multiple_order_error(self):
        orders = self.sale_order + self.sale_order.copy()
        with self.assertRaises(exceptions.UserError):
            orders.write({'timesheet_limit_date': '2019-05-09'})

    def test_multiple_line_pass(self):
        # recomputation can be triggered on lines on different so
        # they hould pass succesfully
        orders = self.sale_order + self.sale_order.copy()
        so_lines = orders.mapped('order_line')
        so_lines._analytic_compute_delivered_quantity_domain()
