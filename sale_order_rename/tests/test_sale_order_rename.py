# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError
from unittest import mock

from odoo.tests import common
from odoo.tools.misc import mute_logger

_ir_sequence_class = 'odoo.addons.base.models.ir_sequence.IrSequence'


class TestSaleOrderRename(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.SaleOrder = self.env['sale.order']
        self.SudoSaleOrder = self.SaleOrder.sudo()

    def test_1(self):
        self.SudoSaleOrder.create({
            'name': 'Test #1',
            'partner_id': self.env.ref('base.res_partner_1').id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.SudoSaleOrder.create({
                'name': 'Test #1',
                'partner_id': self.env.ref('base.res_partner_1').id,
            })

    def test_2(self):
        sale_order_1 = self.SudoSaleOrder.create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        sale_order_2 = self.SudoSaleOrder.create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })

        self.assertNotEqual(sale_order_1.name, sale_order_2.name)

    def test_3(self):
        sale_order_1 = self.SudoSaleOrder.create({
            'name': 'Test #3-1',
            'partner_id': self.env.ref('base.res_partner_1').id,
        })

        with mock.patch(
                _ir_sequence_class + '.next_by_code',
                side_effect=['Test #3-1', 'Test #3-2']):
            sale_order_2 = self.SudoSaleOrder.create({
                'partner_id': self.env.ref('base.res_partner_1').id,
            })

        self.assertNotEqual(sale_order_1.name, sale_order_2.name)
