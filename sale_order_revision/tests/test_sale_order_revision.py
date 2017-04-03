# -*- coding: utf-8 -*-
# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestSaleOrderRevision(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderRevision, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.partner_id = self.env.ref('base.res_partner_2').id
        self.product_id1 = self.env.ref('product.product_product_1').id
        self.sale_order_1 = self._create_sale_order()
        self.action = self._revision_sale_order(self.sale_order_1)
        self.revision_1 = self.sale_order_1.current_revision_id

    def _create_sale_order(self):
        # Creating a sale order
        new_sale = self.sale_order_model.create({
            'partner_id': self.partner_id,
            'order_line': [(0, 0, {
                'product_id': self.product_id1,
                'product_uom_qty': '15.0'
            })]
        })
        return new_sale

    def _revision_sale_order(self, sale_order):
        # Cancel the sale order
        sale_order.action_cancel()
        # Create a new revision
        return sale_order.create_revision()

    def test_order_revision(self):
        """Check revision process"""
        self.assertEquals(self.sale_order_1.unrevisioned_name,
                          self.sale_order_1.name)
        self.assertEquals(self.sale_order_1.state, 'cancel')
        self.assertFalse(self.sale_order_1.active)
        self.assertEquals(self.revision_1.unrevisioned_name,
                          self.sale_order_1.name)
        self.assertEquals(self.revision_1.state, 'draft')
        self.assertTrue(self.revision_1.active)
        self.assertEquals(self.revision_1.old_revision_ids,
                          self.sale_order_1)
        self.assertEquals(self.revision_1.revision_number, 1)
        self.assertEquals(self.revision_1.name.endswith('-01'), True)

        self._revision_sale_order(self.revision_1)
        revision_2 = self.revision_1.current_revision_id

        self.assertEquals(revision_2, self.sale_order_1.current_revision_id)
        self.assertEquals(self.revision_1.state, 'cancel')
        self.assertFalse(self.revision_1.active)
        self.assertEquals(revision_2.unrevisioned_name,
                          self.sale_order_1.name)
        self.assertEquals(revision_2.state, 'draft')
        self.assertTrue(revision_2.active)
        self.assertEquals(revision_2.old_revision_ids,
                          self.sale_order_1 + self.revision_1)
        self.assertEquals(revision_2.revision_number, 2)
        self.assertEquals(revision_2.name.endswith('-02'), True)

    def test_simple_copy(self):
        sale_order_2 = self._create_sale_order()
        self.assertEquals(sale_order_2.name, sale_order_2.unrevisioned_name)
        sale_order_3 = sale_order_2.copy()
        self.assertEquals(sale_order_3.name, sale_order_3.unrevisioned_name)
