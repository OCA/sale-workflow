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

    def _create_sale_order(self):
        # Creating a sale order
        new_sale = self.sale_order_model.create({
            'partner_id': self.partner_id,
            'order_line': [(0, 0, {
                'product_id': self.product_id1,
                'product_uom_qty': '15.0'
            })]
        })
        # Cancel the sale order
        new_sale.action_cancel()
        # Create a new revision
        self.action = new_sale.copy_quotation()
        return new_sale

    def test_order_revision(self):
        """Check whether revision number is 1 or not."""
        self.assertEquals(self.sale_order_1.id, self.action['res_id'])
        if self.sale_order_1.old_revision_ids:
            self.sale_order_1.active = False
        self.assertEquals(self.sale_order_1.revision_number, 1)
        self.assertEquals(self.sale_order_1.name.endswith('-01'), True)
