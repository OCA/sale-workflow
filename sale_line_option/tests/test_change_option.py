# coding: utf-8
# © 2015 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestOptionCase(TransactionCase):

    def test_sale_line_change(self):
        "Check if all required options are refresh when we change the product"
        sale = self.sale_line.order_id
        sol = self.sale_line
        new_product = self.env.ref(
            'sale_line_option.product_pc_assmb_option2').id
        res_onchange_product = self.sale_line.product_id_change(
            sale.pricelist_id.id, new_product, sol.product_uom_qty,
            sol.product_uom.id, sol.product_uos_qty, sol.product_uos.id, '',
            sale.partner_id.id, False, False, sale.date_order,
            False, sale.fiscal_position, True)
        bom_opt2 = self.env.ref('sale_line_option.bom_pc_assmb_option2')
        bom_products = [x.product_id.id
                        for x in bom_opt2.bom_line_ids
                        if x.default_qty > 0]
        _logger.debug('  >>> Bom product ids: %s', bom_products)
        onchange_value = res_onchange_product['value'].get(
            'option_ids')
        self.assertTrue(len(onchange_value) > 0)
        opt_products = [x[2]['product_id'] for x in onchange_value]
        _logger.debug('  >>> Options product ids: %s', opt_products)
        self.assertTrue(len(bom_products) > 0)
        self.assertTrue(len(opt_products) > 0)
        if bom_products and opt_products:
            self.assertEqual(set(bom_products), set(opt_products))

    def test_check_option_line_when_bom_change(self):
        "Check if remove bom.line have no impact on option lines"
        bom_line = self.env.ref('sale_line_option.bom_line_pc_assmb_option13')
        product_id = bom_line.product_id.id
        bom_line.unlink()
        option = [x for x in self.sale_line.option_ids
                  if x.product_id.id == product_id]
        self.assertTrue(len(option) == 1)
        if option:
            self.assertTrue(len(option[0].bom_line_id) == 0)

    def setUp(self):
        super(TestOptionCase, self).setUp()
        self.sale_line = self.env.ref(
            'sale_line_option.sale_order_line_option')
