# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import zipfile
import base64
import tempfile
import pathlib

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    expense_ids = fields.One2many(
        readonly=False,
        domain=['|', ('state', '=', 'approved'), ('state', '=', 'done')])

    def attach_expense_receipt_to_invoice(self, invoice):
        self.ensure_one()
        temp_dir = tempfile.mkdtemp()
        expenses = self.env['hr.expense']
        for line in self.order_line.filtered(
                lambda l: l.is_expense and
                l.product_id.expense_policy == 'cost'):
            expenses |= self.expense_ids.filtered(
                lambda e: e.sheet_id.state == 'post' and
                e.product_id == line.product_id and
                e.unit_amount == line.price_unit)

        attachments = self.env['ir.attachment'].search([
            ('res_id', 'in', expenses.ids)])

        if attachments:
            file_path = pathlib.Path(temp_dir + '/Expense_Receipt.zip')
            receipt_zip_file = zipfile.ZipFile(
                file_path, mode='w')
            for attachment in attachments:
                receipt_zip_file.writestr(attachment.name,
                                          base64.b64decode(attachment.datas))
            receipt_zip_file.close()
            with open(file_path, 'rb') as f:
                datas = base64.b64encode(f.read())

            self.env['ir.attachment'].create({
                'name': 'Expense_Receipt.zip',
                'type': 'binary',
                'datas': datas,
                'datas_fname': 'Expense_Receipt.zip',
                'store_fname': 'Expense_Receipt.zip',
                'res_model': invoice._name,
                'res_id': invoice.id,
                'mimetype': 'application/zip'
            })

        return True

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(
            grouped=False,
            final=False)
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            self.attach_expense_receipt_to_invoice(invoice)
        return invoice_ids
