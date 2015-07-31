# -*- coding: utf-8 -*-
from openerp.tests import common


class test_product_bundle(common.TransactionCase):
    """ Test Product bundle"""

    def setUp(self):
        super(test_product_bundle, self).setUp()
        self.sale_order = self.env['sale.order']
        self.sale_order_bundle = self.env['sale.order.bundle']

    def test_add_bundle(self):
        so = self.env.ref('sale.sale_order_6')
        count_lines = len(so.order_line)
        untaxed_amount = so.amount_untaxed
        tax_amount = so.amount_tax
        total_amount = so.amount_total

        product_bundle = self.env.ref(
            'sale_product_bundle.product_bundle_i5_computer')
        # Simulation the opening of the wizard and adding a bundle on the
        # current sale order
        so_bundle = self.sale_order_bundle.with_context(
            active_id=so.id).create({'product_bundle_id': product_bundle.id,
                                     'quantity': 2})
        so_bundle.add_bundle()
        # checking our sale order
        self.assertEquals(len(so.order_line), count_lines + 4)
        # untaxed_amount + ((147*1)+(2100*1)+(2000*1)+(85*2)) * 2
        self.assertEquals(so.amount_untaxed, untaxed_amount + 8834.0)
        self.assertEquals(so.amount_tax, tax_amount + 0)  # without tax
        self.assertEquals(so.amount_total, total_amount + 8834.0)
        sequence = {}
        for line in so.order_line:
            sequence[line.product_id.id] = line.sequence
            for bundle_line in product_bundle.bundle_line_ids:
                if line.product_id.id == bundle_line.product_id.id:
                    self.assertEquals(line.product_id.name,
                                      bundle_line.product_id.name)
        # make sure sale order line sequence keep sequence set on bundle
        seq_line1 = sequence.pop(
            self.env.ref(
                "sale_product_bundle.product_bundle_line_computer_2"
            ).product_id.id)
        seq_line2 = sequence.pop(
            self.env.ref(
                "sale_product_bundle.product_bundle_line_computer_4"
            ).product_id.id)
        seq_line3 = sequence.pop(
            self.env.ref(
                "sale_product_bundle.product_bundle_line_computer_1"
            ).product_id.id)
        seq_line4 = sequence.pop(
            self.env.ref(
                "sale_product_bundle.product_bundle_line_computer_3"
            ).product_id.id)
        self.assertTrue(max([v for k, v in sequence.iteritems()]) <
                        seq_line1 < seq_line2 < seq_line3 < seq_line4)

    def test_add_bundle_on_empty_so(self):
        so = self.sale_order.create({
            'partner_id': self.ref('base.res_partner_1')})
        product_bundle = self.env.ref(
            'sale_product_bundle.product_bundle_i5_computer')
        so_bundle = self.sale_order_bundle.with_context(
            active_id=so.id).create({'product_bundle_id': product_bundle.id,
                                     'quantity': 2})
        so_bundle.add_bundle()
        self.assertEquals(len(so.order_line), 4)
