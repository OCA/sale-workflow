# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp.tools import float_is_zero
import logging

logger = logging.getLogger(__name__)


class SaleOrderImport(models.TransientModel):
    _name = 'sale.order.import'
    _inherit = ['sale.order.import', 'base.ubl']

    @api.model
    def parse_xml_order(self, xml_root, detect_doc_type=False):
        start_tag = '{urn:oasis:names:specification:ubl:schema:xsd:'
        rfq = 'RequestForQuotation'
        if xml_root.tag == start_tag + 'Order-2}Order':
            if detect_doc_type:
                return 'order'
            else:
                return self.parse_ubl_sale_order(xml_root)
        elif xml_root.tag == '%s%s-2}%s' % (start_tag, rfq, rfq):
            if detect_doc_type:
                return 'rfq'
            else:
                return self.parse_ubl_sale_order(xml_root)
        else:
            return super(SaleOrderImport, self).parse_xml_order(xml_root)

    @api.model
    def parse_ubl_sale_order_line(self, line, ns):
        qty_prec = self.env['decimal.precision'].precision_get('Product UoS')
        line_item = line.xpath('cac:LineItem', namespaces=ns)[0]
        # line_id_xpath = line_item.xpath('cbc:ID', namespaces=ns)
        # line_id = line_id_xpath[0].text
        qty_xpath = line_item.xpath('cbc:Quantity', namespaces=ns)
        qty = float(qty_xpath[0].text)
        price_unit = 0.0
        subtotal_without_tax_xpath = line_item.xpath(
            'cbc:LineExtensionAmount', namespaces=ns)
        if subtotal_without_tax_xpath:
            subtotal_without_tax = float(subtotal_without_tax_xpath[0].text)
            if not float_is_zero(qty, precision_digits=qty_prec):
                price_unit = subtotal_without_tax / qty
        else:
            price_xpath = line_item.xpath(
                'cac:Price/cbc:PriceAmount', namespaces=ns)
            if price_xpath:
                price_unit = float(price_xpath[0].text)
        res_line = {
            'product': self.ubl_parse_product(line_item, ns),
            'qty': qty,
            'uom': {'unece_code': qty_xpath[0].attrib.get('unitCode')},
            'price_unit': price_unit,
            }
        return res_line

    @api.model
    def parse_ubl_sale_order(self, xml_root):
        ns = xml_root.nsmap
        main_xmlns = ns.pop(None)
        ns['main'] = main_xmlns
        if 'RequestForQuotation' in main_xmlns:
            root_name = 'main:RequestForQuotation'
            line_name = 'cac:RequestForQuotationLine'
            doc_type = 'rfq'
        elif 'Order' in main_xmlns:
            root_name = 'main:Order'
            line_name = 'cac:OrderLine'
            doc_type = 'order'
        date_xpath = xml_root.xpath(
            '/%s/cbc:IssueDate' % root_name, namespaces=ns)
        currency_code = False
        for cur_node_name in ('DocumentCurrencyCode', 'PricingCurrencyCode'):
            currency_xpath = xml_root.xpath(
                '/%s/cbc:%s' % (root_name, cur_node_name), namespaces=ns)
            if currency_xpath:
                currency_code = currency_xpath[0].text
                break
        if not currency_code:
            currency_xpath = xml_root.xpath(
                '//cbc:LineExtensionAmount', namespaces=ns)
            if currency_xpath:
                currency_code = currency_xpath[0].attrib.get('currencyID')
        order_ref_xpath = xml_root.xpath(
            '/%s/cbc:ID' % root_name, namespaces=ns)
        customer_xpath = xml_root.xpath(
            '/%s/cac:BuyerCustomerParty' % root_name, namespaces=ns)
        if not customer_xpath:
            customer_xpath = xml_root.xpath(
                '/%s/cac:OriginatorCustomerParty' % root_name, namespaces=ns)
        customer_dict = self.ubl_parse_customer_party(customer_xpath[0], ns)
        delivery_xpath = xml_root.xpath(
            '/%s/cac:Delivery' % root_name, namespaces=ns)
        shipping_dict = {}
        if delivery_xpath:
            shipping_dict = self.ubl_parse_delivery(delivery_xpath[0], ns)
        # In the demo UBL 2.1 file, they use 'IMCOTERM'... but I guess
        # it's a mistake and they should use 'INCOTERM'
        # So, for the moment, I ignore the attributes in the xpath for incoterm
        delivery_term_xpath = xml_root.xpath(
            "/%s/cac:DeliveryTerms" % root_name, namespaces=ns)
        if delivery_term_xpath:
            incoterm_dict = self.ubl_parse_incoterm(delivery_term_xpath[0], ns)
        else:
            incoterm_dict = {}
        note_xpath = xml_root.xpath(
            '/%s/cbc:Note' % root_name, namespaces=ns)
        lines_xpath = xml_root.xpath(
            '/%s/%s' % (root_name, line_name), namespaces=ns)
        res_lines = []
        for line in lines_xpath:
            res_lines.append(self.parse_ubl_sale_order_line(line, ns))
        # TODO : add charges
        res = {
            'partner': customer_dict,
            'ship_to': shipping_dict,
            'currency': {'iso': currency_code},
            'date': date_xpath[0].text,
            'order_ref': order_ref_xpath[0].text,
            'incoterm': incoterm_dict,
            'note': note_xpath and note_xpath[0].text or False,
            'lines': res_lines,
            'doc_type': doc_type,
        }
        # Stupid hack to remove invalid VAT of sample files
        if res['partner']['vat'] in ['SE1234567801', '12356478', 'DK12345678']:
            res['partner'].pop('vat')
        return res
