# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tools import file_open
import base64


class TestUblOrderImport(TransactionCase):

    def test_ubl_order_import(self):
        tests = {
            'UBL-Order-2.1-Example.xml': {
                'client_order_ref': '34',
                'date_order': '2010-01-20',
                'partner': self.env.ref('sale_order_import_ubl.johnssons'),
                'shipping_partner':
                self.env.ref('sale_order_import_ubl.swedish_trucking'),
                'currency': self.env.ref('base.SEK'),
                },
            'UBL-Order-2.0-Example.xml': {
                'client_order_ref': 'AEG012345',
                'date_order': '2010-06-20',
                'partner': self.env.ref('sale_order_import_ubl.iyt'),
                'shipping_partner':
                self.env.ref('sale_order_import_ubl.fred_churchill'),
                'currency': self.env.ref('base.GBP'),
                },
            'UBL-RequestForQuotation-2.0-Example.xml': {
                'partner': self.env.ref('sale_order_import_ubl.terminus'),
                'shipping_partner':
                self.env.ref('sale_order_import_ubl.s_massiah'),
                },
            'UBL-RequestForQuotation-2.1-Example.xml': {
                'partner':
                self.env.ref('sale_order_import_ubl.gentofte_kommune'),
                'currency': self.env.ref('base.DKK'),
                'shipping_partner': self.env.ref(
                    'sale_order_import_ubl.delivery_gentofte_kommune'),
                },
            }
        for filename, res in tests.iteritems():
            f = file_open(
                'sale_order_import_ubl/tests/files/' + filename, 'rb')
            xml_file = f.read()
            wiz = self.env['sale.order.import'].create({
                'order_file': base64.b64encode(xml_file),
                'order_filename': filename,
            })
            f.close()
            action = wiz.import_order_button()
            so = self.env['sale.order'].browse(action['res_id'])
            self.assertEqual(
                so.partner_id.commercial_partner_id,
                res['partner'])
            if res.get('currency'):
                self.assertEqual(so.currency_id, res['currency'])
            if res.get('client_order_ref'):
                self.assertEqual(so.client_order_ref, res['client_order_ref'])
            if res.get('date_order'):
                self.assertEqual(so.date_order[:10], res['date_order'])
            if res.get('shipping_partner'):
                self.assertEqual(
                    so.partner_shipping_id, res['shipping_partner'])
