# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tools import file_open
import base64


class TestCsvOrderImport(TransactionCase):

    def test_csv_order_import(self):
        filename = 'order_file_test1.csv'
        f = file_open(
            'sale_order_import_csv/tests/files/' + filename, 'rb')
        csv_file = f.read()
        partner = self.env.ref('base.res_partner_2')
        wiz = self.env['sale.order.import'].create({
            'order_file': base64.b64encode(csv_file),
            'order_filename': filename,
            'partner_id': partner.id,
        })
        f.close()
        action = wiz.import_order_button()
        so = self.env['sale.order'].browse(action['res_id'])
        self.assertEqual(so.partner_id, partner)
        self.assertEqual(len(so.order_line), 3)
