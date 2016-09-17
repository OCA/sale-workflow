# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestUblOrderImport(TransactionCase):

    def test_ubl_generate(self):
        ro = self.registry['report']
        soo = self.env['sale.order']
        buo = self.env['base.ubl']
        quotation_states = soo.get_quotation_states()
        order_states = soo.get_order_states()
        for i in range(7):
            i += 1
            order = self.env.ref('sale.sale_order_%d' % i)
            for version in ['2.0', '2.1']:
                # I didn't manage to make it work with new api :-(
                pdf_file = ro.get_pdf(
                    self.cr, self.uid, order.ids, 'sale.report_saleorder',
                    context={'ubl_version': version})
                res = buo.get_xml_files_from_pdf(pdf_file)
                if order.state in quotation_states:
                    filename = order.get_ubl_filename(
                        'quotation', version=version)
                    self.assertTrue(filename in res)
                elif order.state in order_states:
                    filename = order.get_ubl_filename('order', version=version)
                    self.assertTrue(filename in res)
