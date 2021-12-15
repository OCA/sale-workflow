# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleTimesheetProjectLink(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetProjectLink, cls).setUpClass()
        cls.Product = cls.env['product.product']
        cls.Project = cls.env['project.project']
        cls.SaleOrder = cls.env['sale.order']

        cls.project_1 = cls.Project.create({
            'name': "Test Project 1",
        })
        cls.project_2 = cls.Project.create({
            'name': "Test Project 2",
        })

        cls.flat_fee_product = cls.Product.create({
            'name': "Flat Fee Product",
            'type': 'service',
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_new_project',
            'list_price': '120',
            'standard_price': '80',
        })

        cls.fixed_project_product = cls.Product.create({
            'name': "Fixed project Product",
            'type': 'service',
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': cls.project_1.id,
            'list_price': '120',
            'standard_price': '80',
        })

        cls.partner_agrolait = cls.env.ref('base.res_partner_2')

    def test_compute_all_projects(self):
        partner = self.partner_agrolait
        flat_fee_product = self.flat_fee_product
        fixed_project_product = self.fixed_project_product

        so = self.SaleOrder.create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': "Flat Fee",
                    'product_id': flat_fee_product.id,
                    'product_uom_qty': flat_fee_product.uom_id.id,
                    'price_unit': flat_fee_product.list_price,
                }),
                (0, 0, {
                    'name': "Fixed project",
                    'product_id': fixed_project_product.id,
                    'product_uom_qty': fixed_project_product.uom_id.id,
                    'price_unit': fixed_project_product.list_price,
                }),
            ]
        })

        so.action_confirm()
        self.assertEquals(len(so.get_linked_projects()), 2)
        self.assertEquals(so.linked_projects_count, 2)

        so.analytic_account_id = self.project_2.analytic_account_id
        so.invalidate_cache()
        self.assertEquals(len(so.get_linked_projects()), 3)
        self.assertEquals(so.linked_projects_count, 3)
