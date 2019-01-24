# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestOptionCase(TransactionCase):

    def test10_product_qty(self):
        qties = {
            x.product_id: x.opt_default_qty
            for x in self.env.ref(
                'sale_line_option.bom_pc_assmb_option1').bom_line_ids}
        for line in self.sale_line.option_ids:
            self.assertTrue(
                line.qty == qties[line.product_id],
                "Option qty error on product %s" % line.product_id.name)

    def test20_sale_line_change(self):
        "Check if all required options are refresh when we change the product"
        # We have 3 options
        self.assertTrue(len(self.sale_line.option_ids) == 3,
                        "options number is wrong in %s %s" % (
                            self.sale_line, self.sale_line.order_id.name))
        new_product = self.env.ref('sale_line_option.product_pc_assmb_option2')
        self.sale_line.product_id = new_product.id
        self.sale_line.product_id_change()
        # we now have only 2 options
        self.assertTrue(len(self.sale_line.option_ids) == 2,
                        "options number is wrong in %s %s" % (
                            self.sale_line, self.sale_line.order_id.name))
        option_products = [x.product_id for x in self.sale_line.option_ids]
        _logger.debug('  >>> Options product ids: %s',
                      [x.name for x in option_products])
        bom_opt = self.env.ref('sale_line_option.bom_pc_assmb_option2')
        bom_products = [x.product_id
                        for x in bom_opt.bom_line_ids
                        if x.opt_default_qty > 0]
        _logger.debug('  >>> Bom product ids: %s',
                      [x.name for x in bom_products])
        self.assertTrue(len(bom_products) > 0,
                        "%s bom shouldn't be null" % bom_products)
        if bom_products and option_products:
            self.assertEqual(set(bom_products), set(option_products),
                             "Bom and option products should be identical")

    def test30_check_option_line_when_bom_change(self):
        "Check if remove bom.line have no impact on option lines"
        bom_line = self.env.ref('sale_line_option.bom_line_pc_assmb_option13')
        product = bom_line.product_id
        bom_line.unlink()
        option = [x for x in self.sale_line.option_ids
                  if x.product_id == product]
        self.assertTrue(len(option) == 1,
                        "We should have 1 option %s" % option)
        if option:
            self.assertTrue(len(option[0].bom_line_id) == 0,
                            "Option bom_line %s should be null"
                            % option[0].bom_line_id)

    def setUp(self):
        super(TestOptionCase, self).setUp()
        self.sale_line = self.env.ref(
            'sale_line_option.sale_order_line_option')
