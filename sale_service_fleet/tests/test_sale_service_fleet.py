# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestSaleServiceFleet(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestSaleServiceFleet, self).setUp()

        self.product_template_revision = self.env.ref(
            'sale_service_project.product_template_revision_1')
        self.product_revision = self.env['product.product'].search(
            [('product_tmpl_id', '=', self.product_template_revision.id)])
        self.product_stock = self.env.ref('product.product_product_4')
        self.vehicle = self.env.ref('fleet.vehicle_1')
        self.product_cost_service = self.env.ref(
            'product.product_product_consultant')
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.partner = self.env.ref('base.res_partner_2')

        self.price_list = self.env.ref('product.list0')

        self.sale_order_manual = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_policy': 'manual',
            'pricelist_id': self.price_list.id,
            'vehicle_id': self.vehicle.id
        })
        self.sale_order_line.create(
            {'product_id': self.product_revision.id,
             'product_uos_qty': 1,
             'price_unit': self.product_revision.list_price,
             'order_id': self.sale_order_manual.id,
             'name': self.product_revision.name})

    def test_sale_order_fleet(self):
        # Confirm the sale order
        self.sale_order_manual.action_button_confirm()

        # Search task generate by sale order
        task = self.env['project.task'].search(
            [('sale_line_id', '=', self.sale_order_manual.order_line[0].id)])
        self.assertTrue(task)
        self.assertEqual(task.vehicle_id.id, self.vehicle.id)
        self.assertEqual(task.project_id.vehicle_id.id, self.vehicle.id)
