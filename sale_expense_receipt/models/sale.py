# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import pathlib
import tempfile
import zipfile
from base64 import b64decode

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    expense_ids = fields.One2many(
        readonly=False, domain=["|", ("state", "=", "approved"), ("state", "=", "done")]
    )

    def attach_expense_receipt_to_invoice(self, invoice):
        self.ensure_one()
        temp_dir = tempfile.mkdtemp()
        expenses = self.env["hr.expense"]
        for line in self.order_line.filtered(
            lambda l: l.is_expense and l.product_id.expense_policy == "cost"
        ):
            expenses |= self.expense_ids.filtered(
                lambda e: e.sheet_id.state == "post"
                and e.product_id.id == line.product_id.id
                and e.unit_amount == line.price_unit
            )

        attachments = self.env["ir.attachment"].search([("res_id", "in", expenses.ids)])
        if attachments:
            file_path = pathlib.Path(temp_dir + "/Expense_Receipt.zip")
            receipt_zip_file = zipfile.ZipFile(file_path, mode="w")
            for attachment in attachments:
                receipt_zip_file.writestr(
                    attachment.name, b64decode(attachment.datas)
                )
            receipt_zip_file.close()
            with open(file_path, "rb") as f:
                datas = b64decode(f.read())
            self.env["ir.attachment"].create(
                {
                    "name": "Expense_Receipt.zip",
                    "type": "binary",
                    "datas": datas,
                    "store_fname": "Expense_Receipt.zip",
                    "res_model": invoice._name,
                    "res_id": invoice.id,
                    "mimetype": "application/zip",
                }
            )

        return True

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoice_ids = super(SaleOrder, self)._create_invoices(
            grouped=grouped, final=final, date=date
        )
        for invoice in invoice_ids:
            self.attach_expense_receipt_to_invoice(invoice)
        return invoice_ids
