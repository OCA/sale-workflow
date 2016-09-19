# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'base.ubl']

    @api.model
    def get_quotation_states(self):
        return ['draft', 'sent']

    @api.model
    def get_order_states(self):
        return [
            'waiting_date', 'progress', 'manual',
            'shipping_except', 'invoice_except', 'done']

    @api.multi
    def _ubl_add_header(self, doc_type, parent_node, ns, version='2.1'):
        now_utc = fields.Datetime.now()
        date = now_utc[:10]
        time = now_utc[11:]
        ubl_version = etree.SubElement(
            parent_node, ns['cbc'] + 'UBLVersionID')
        ubl_version.text = version
        doc_id = etree.SubElement(parent_node, ns['cbc'] + 'ID')
        doc_id.text = self.name
        issue_date = etree.SubElement(parent_node, ns['cbc'] + 'IssueDate')
        issue_date.text = date
        if doc_type == 'quotation':
            issue_time = etree.SubElement(parent_node, ns['cbc'] + 'IssueTime')
            issue_time.text = time
        if self.note:
            note = etree.SubElement(parent_node, ns['cbc'] + 'Note')
            note.text = self.note
        if doc_type == 'quotation':
            doc_currency = etree.SubElement(
                parent_node, ns['cbc'] + 'PricingCurrencyCode')
            doc_currency.text = self.currency_id.name

    @api.multi
    def _ubl_add_quoted_monetary_total(self, parent_node, ns, version='2.1'):
        monetary_total = etree.SubElement(
            parent_node, ns['cac'] + 'QuotedMonetaryTotal')
        line_total = etree.SubElement(
            monetary_total, ns['cbc'] + 'LineExtensionAmount',
            currencyID=self.currency_id.name)
        line_total.text = unicode(self.amount_untaxed)
        tax_inclusive_amount = etree.SubElement(
            monetary_total, ns['cbc'] + 'TaxInclusiveAmount',
            currencyID=self.currency_id.name)
        tax_inclusive_amount.text = unicode(self.amount_total)
        payable_amount = etree.SubElement(
            monetary_total, ns['cbc'] + 'PayableAmount',
            currencyID=self.currency_id.name)
        payable_amount.text = unicode(self.amount_total)

    @api.multi
    def _ubl_add_quotation_line(
            self, parent_node, oline, line_number, ns, version='2.1'):
        line_root = etree.SubElement(
            parent_node, ns['cac'] + 'QuotationLine')
        dpo = self.env['decimal.precision']
        qty_precision = dpo.precision_get('Product UoS')
        price_precision = dpo.precision_get('Product Price')
        self._ubl_add_line_item(
            line_number, oline.name, oline.product_id, 'sale',
            oline.product_uom_qty, oline.product_uom, line_root, ns,
            currency=self.currency_id, price_subtotal=oline.price_subtotal,
            qty_precision=qty_precision, price_precision=price_precision,
            version=version)

    @api.multi
    def generate_quotation_ubl_xml_etree(self, version='2.1'):
        nsmap, ns = self._ubl_get_nsmap_namespace(
            'Quotation-2', version=version)
        xml_root = etree.Element('Quotation', nsmap=nsmap)
        doc_type = 'quotation'
        self._ubl_add_header(doc_type, xml_root, ns, version=version)

        self._ubl_add_supplier_party(
            False, self.company_id, 'SellerSupplierParty', xml_root, ns,
            version=version)
        if version == '2.1':
            self._ubl_add_customer_party(
                self.partner_id, False, 'BuyerCustomerParty', xml_root, ns,
                version=version)
        self._ubl_add_delivery(
            self.partner_shipping_id, xml_root, ns, version=version)
        if hasattr(self, 'incoterm') and self.incoterm:
            self._ubl_add_delivery_terms(
                self.incoterm, xml_root, ns, version=version)
        self._ubl_add_quoted_monetary_total(xml_root, ns, version=version)

        line_number = 0
        for oline in self.order_line:
            line_number += 1
            self._ubl_add_quotation_line(
                xml_root, oline, line_number, ns, version=version)
        return xml_root

    @api.multi
    def generate_order_response_simple_ubl_xml_etree(self, version='2.1'):
        nsmap, ns = self._ubl_get_nsmap_namespace(
            'OrderResponseSimple-2', version=version)
        xml_root = etree.Element('OrderResponseSimple', nsmap=nsmap)
        doc_type = 'order'
        self._ubl_add_header(doc_type, xml_root, ns, version=version)

        accepted_indicator = etree.SubElement(
            xml_root, ns['cbc'] + 'AcceptedIndicator')
        accepted_indicator.text = 'true'
        order_reference = etree.SubElement(
            xml_root, ns['cac'] + 'OrderReference')
        order_reference_id = etree.SubElement(
            order_reference, ns['cbc'] + 'ID')
        order_reference_id.text = self.client_order_ref or 'Missing'
        self._ubl_add_supplier_party(
            False, self.company_id, 'SellerSupplierParty', xml_root, ns,
            version=version)
        self._ubl_add_customer_party(
            self.partner_id, False, 'BuyerCustomerParty', xml_root, ns,
            version=version)
        return xml_root

    @api.multi
    def generate_ubl_xml_string(self, doc_type, version='2.1'):
        self.ensure_one()
        assert doc_type in ('quotation', 'order'), 'wrong doc_type'
        logger.debug('Starting to generate UBL XML %s file', doc_type)
        lang = self.get_ubl_lang()
        # The aim of injecting lang in context
        # is to have the content of the XML in the partner's lang
        # but the problem is that the error messages will also be in
        # that lang. But the error messages should almost never
        # happen except the first days of use, so it's probably
        # not worth the additionnal code to handle the 2 langs
        if doc_type == 'quotation':
            xml_root = self.with_context(lang=lang).\
                generate_quotation_ubl_xml_etree(version=version)
            document = 'Quotation'
        elif doc_type == 'order':
            xml_root = self.with_context(lang=lang).\
                generate_order_response_simple_ubl_xml_etree(version=version)
            document = 'OrderResponseSimple'
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True)
        self._ubl_check_xml_schema(xml_string, document, version=version)
        logger.debug(
            '%s UBL XML file generated for sale order ID %d (state %s)',
            doc_type, self.id, self.state)
        logger.debug(xml_string)
        return xml_string

    @api.multi
    def get_ubl_filename(self, doc_type, version='2.1'):
        """This method is designed to be inherited"""
        if doc_type == 'quotation':
            return 'UBL-Quotation-%s.xml' % version
        elif doc_type == 'order':
            return 'UBL-OrderResponseSimple-%s.xml' % version

    @api.multi
    def get_ubl_version(self):
        version = self._context.get('ubl_version') or '2.1'
        return version

    @api.multi
    def get_ubl_lang(self):
        return self.partner_id.lang or 'en_US'

    @api.multi
    def embed_ubl_xml_in_pdf(self, pdf_content):
        self.ensure_one()
        doc_type = False
        if self.state in self.get_quotation_states():
            doc_type = 'quotation'
        elif self.state in self.get_order_states():
            doc_type = 'order'
        if doc_type:
            version = self.get_ubl_version()
            ubl_filename = self.get_ubl_filename(doc_type, version=version)
            xml_string = self.generate_ubl_xml_string(
                doc_type, version=version)
            pdf_content = self.embed_xml_in_pdf(
                xml_string, ubl_filename, pdf_content)
        return pdf_content
