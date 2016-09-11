# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
import logging

logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(
            self, cr, uid, ids, report_name, html=None, data=None,
            context=None):
        """We go through that method when the PDF is generated for the 1st
        time and also when it is read from the attachment.
        This method is specific to QWeb"""
        if context is None:
            context = {}
        pdf_content = super(Report, self).get_pdf(
            cr, uid, ids, report_name, html=html, data=data, context=context)
        if (
                report_name == 'sale.report_saleorder' and
                len(ids) == 1 and
                not context.get('no_embedded_ubl_xml')):
            order = self.pool['sale.order'].browse(
                cr, uid, ids[0], context=context)
            pdf_content = order.embed_ubl_xml_in_pdf(
                pdf_content)
        return pdf_content
