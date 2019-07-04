# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import TestCommonMixin


class TestSale(TestCommonMixin):

    def test_domain_timesheet_limit_date(self):
        self.sale_order.timesheet_limit_date = self.date_09
        domain = self.so_line._timesheet_compute_delivered_quantity_domain()
        found = self.aal_model.search(domain).mapped('date')
        self.assertTrue(
            all([f <= self.date_09 for f in found])
        )

    def test_delivered_limited(self):
        # lines linked to SO based on limit date
        self.sale_order.timesheet_limit_date = '2019-05-09'
        self.assertEqual(self.so_line.qty_delivered, 2)
        self.assertEqual(len(self.sale_order.timesheet_ids), 2)
        self.sale_order.timesheet_limit_date = '2019-05-08'
        self.assertEqual(self.so_line.qty_delivered, 1)
        self.sale_order.timesheet_limit_date = '2019-05-07'
        self.assertEqual(self.so_line.qty_delivered, 0)
        # restored
        self.sale_order.timesheet_limit_date = False
        self.assertEqual(self.so_line.qty_delivered, 3)

    def test_multiple_orders_pass(self):
        # recomputation can be triggered on lines from different SO
        # the result should be computed on each SO independently
        orders = self.sale_order
        self.sale_order.timesheet_limit_date = '2019-05-09'
        # create and initialize second order
        order_2 = orders.copy()
        orders += order_2
        order_2.timesheet_limit_date = '2019-05-08'
        new_task = self.env['project.task'].create({
            'name': 'Test',
            'sale_line_id': order_2.order_line[0].id
        })
        new_lines = self.aal_model
        new_lines += self.create_analytic_line(
            unit_amount=1,
            date='2019-05-08',
            task_id=new_task.id,
        )
        new_lines += self.create_analytic_line(
            unit_amount=1,
            date='2019-05-10',
            task_id=new_task.id,
        )
        new_lines.write({'so_line': order_2.order_line[0].id})
        order_2.analytic_account_id = self.aaa_model.create({
            'name': 'New Acc.'
        })
        order_2.action_confirm()
        so_lines = self.sale_order.mapped('order_line')
        so_lines += order_2.mapped('order_line')

        # orders get quantity and lines independently
        self.assertEqual(len(self.sale_order.timesheet_ids), 2)
        self.assertEqual(len(order_2.timesheet_ids), 1)
        self.assertEqual(self.so_line.qty_delivered, 2)
        self.assertEqual(order_2.order_line.qty_delivered, 1)
        # change of limit date triggers recomputation
        orders.write({'timesheet_limit_date': '2019-05-10'})
        self.assertEqual(self.so_line.qty_delivered, 3)
        self.assertEqual(order_2.order_line.qty_delivered, 2)
        self.assertEqual(len(order_2.timesheet_ids), 2)
