# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tools import file_open, float_compare
import base64
import unicodecsv


class TestCsvOrderImport(TransactionCase):

    def read_csv_and_create_wizard(self, filename, partner):
        soio = self.env['sale.order.import']
        f = file_open(
            'sale_order_import_csv/tests/files/' + filename, 'rb')
        csv_file = f.read()
        csv_file_content = {}
        f.seek(0)
        reader = unicodecsv.reader(f, delimiter=';', encoding='utf-8')
        for line in reader:
            csv_file_content[line[0]] = float(line[1])
        wiz = soio.create({
            'order_file': base64.b64encode(csv_file),
            'order_filename': filename,
            'partner_id': partner.id,
        })
        f.close()
        return csv_file_content, wiz

    def check_sale_order(self, order, csv_file_content, partner):
        precision = self.env['decimal.precision'].precision_get('Product UoS')
        self.assertEqual(order.partner_id, partner)
        self.assertEqual(len(order.order_line), len(csv_file_content))
        for oline in order.order_line:
            self.assertFalse(
                float_compare(
                    csv_file_content[oline.product_id.default_code],
                    oline.product_uom_qty,
                    precision_digits=precision))

    def test_csv_order_import(self):
        # create new quote
        filename = 'order_file_test1.csv'
        partner = self.env.ref('base.res_partner_2')
        csv_file_content, wiz = self.read_csv_and_create_wizard(
            filename, partner)
        action = wiz.import_order_button()
        so = self.env['sale.order'].browse(action['res_id'])
        self.check_sale_order(so, csv_file_content, partner)
        # update existing quote
        filename_up = 'order_file_test1_update.csv'
        csv_file_content_up, wiz_up = self.read_csv_and_create_wizard(
            filename_up, partner)
        action_up1 = wiz_up.import_order_button()
        self.assertEqual(action_up1['res_model'], 'sale.order.import')
        self.assertEqual(wiz_up.sale_id, so)
        action_up2 = wiz_up.update_order_button()
        self.assertEqual(action_up2['res_model'], 'sale.order')
        self.check_sale_order(so, csv_file_content_up, partner)
