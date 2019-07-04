# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase
from odoo import fields


class TestCommonMixin(SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.aaa_model = cls.env['account.analytic.account']
        cls.aal_model = cls.env['account.analytic.line']
        cls.so_model = cls.env['sale.order']
        cls.so_line_model = cls.env['sale.order.line']
        cls.project_task_model = cls.env['project.task']
        cls.project_project_model = cls.env['project.project']
        cls.analytic_account = cls.aaa_model.create({'name': 'Test Acc.'})
        cls.project = cls.project_project_model.create(
            {'name': "Project Test"}
        )
        cls.product = cls.env['product.product'].create(
            {
                'name': "Service delivered",
                'standard_price': 10,
                'list_price': 20,
                'type': 'service',
                'invoice_policy': 'delivery',
                'uom_id': cls.env.ref('uom.product_uom_hour').id,
                'uom_po_id': cls.env.ref('uom.product_uom_hour').id,
                'default_code': 'SERV-DELI2',
                'service_type': 'timesheet',
                'service_tracking': 'task_global_project',
                'project_id': cls.project.id,
                'taxes_id': False,
            }
        )
        cls.sale_order = cls.so_model.create(
            {
                'partner_id': cls.env.ref('base.main_partner').id,
                'picking_policy': 'direct',
                'pricelist_id': cls.env.ref('product.list0').id,
                'analytic_account_id': cls.project.analytic_account_id.id,
                # in case sale_exception is in place
                'ignore_exception': True,
            }
        )
        product_line = {
            'name': cls.product.name,
            'order_id': cls.sale_order.id,
            'product_id': cls.product.id,
            'product_uom_qty': 1,
            'product_uom': cls.product.uom_id.id,
            'price_unit': cls.product.list_price,
        }
        cls.so_line = cls.so_line_model.create(product_line)
        # action_confirm create the project for us
        cls.sale_order.action_confirm()
        cls.task = cls.project_task_model.search(
            [('sale_line_id', '=', cls.so_line.id)]
        )
        cls.date_08 = fields.Date.from_string('2019-05-08')
        cls.date_09 = fields.Date.from_string('2019-05-09')
        cls.date_10 = fields.Date.from_string('2019-05-10')
        cls.lines = cls.create_analytic_line(unit_amount=1, date='2019-05-10')
        cls.lines += cls.create_analytic_line(unit_amount=1, date='2019-05-09')
        cls.lines += cls.create_analytic_line(unit_amount=1, date='2019-05-08')

    @classmethod
    def create_analytic_line(cls, **kw):
        values = {
            'name': cls.project.name + cls.task.name,
            'project_id': cls.project.id,
            'unit_amount': 0,
            'task_id': cls.task.id,
        }
        values.update(kw)
        return cls.aal_model.create(values)
