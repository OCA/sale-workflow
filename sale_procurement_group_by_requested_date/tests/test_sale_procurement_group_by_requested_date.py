# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields
import datetime


class TestSaleMultiPickingByRequestedDate(TransactionCase):
    """Check the _get_shipped method of Sale Order. """

    def setUp(self):
        """Setup a Sale Order with 4 lines.
        And prepare procurements
        """
        super(TestSaleMultiPickingByRequestedDate, self).setUp()
        sale_obj = self.env['sale.order']
        self.proc_obj = self.env['procurement.order']
        self.proc_group_obj = self.env['procurement.group']
        order_line = self.env['sale.order.line']
        Product = self.env['product.product']
        p1 = Product.create({'name': 'p1', 'type': 'product'}).id
        today = datetime.datetime.now()
        self.dt1 = today
        self.dt2 = today + datetime.timedelta(days=1)

        self.sale1 = sale_obj.create({'partner_id': 1})
        self.sale_line1 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale1.id,
            'requested_date': self.dt1
        })
        self.sale_line2 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale1.id,
            'requested_date': self.dt2
        })
        self.sale_line3 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale1.id,
            'requested_date': self.dt1
        })
        self.sale_line4 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale1.id,
            'requested_date': self.dt2
        })

        self.sale2 = sale_obj.create({'partner_id': 1})
        self.sale_line5 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale2.id,
            'requested_date': self.dt1
        })
        self.sale_line6 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale2.id,
            'requested_date': self.dt1
        })
        self.sale_line7 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale2.id,
            'requested_date': self.dt1
        })
        self.sale_line8 = order_line.create({
            'product_id': p1,
            'name': 'cool product',
            'order_id': self.sale2.id,
            'requested_date': self.dt1
        })

    def test_number_of_groups(self):
        """True when the number of groups created matches the
        result of multiply the different warehouses with the different
        requested dates"""
        self.sale1.action_confirm()
        req_date = fields.Date.to_string(self.dt1)
        g_name = self.sale1.name + '/' + req_date
        groups = self.proc_group_obj.search([('name', '=', g_name)])

        for group in groups:
            if group.name == g_name:
                procurements = self.proc_obj.search([
                    ('group_id', '=', group.id)])
                self.assertEqual(len(procurements), 2)
        self.assertEqual(len(groups), 1)

        req_date2 = fields.Date.to_string(self.dt2)
        g_name = self.sale1.name + '/' + req_date2
        groups = self.proc_group_obj.search([('name', '=', g_name)])

        for group in groups:
            if group.name == g_name:
                procurements = self.proc_obj.search([
                    ('group_id', '=', group.id)])
                self.assertEqual(len(procurements), 2)
        self.assertEqual(len(groups), 1)

        self.sale2.action_confirm()
        g_name = self.sale2.name + '/' + req_date
        groups = self.proc_group_obj.search([('name', '=', g_name)])
        for group in groups:
            if group.name == g_name:
                procurements = self.proc_obj.search([
                    ('group_id', '=', group.id)])
                self.assertEqual(len(procurements), 4)
        self.assertEqual(len(groups), 1)
