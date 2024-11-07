# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_document_attachment = fields.Binary(copy=False, attachment=True)
    sale_document_filename = fields.Char(copy=False)

    def _get_sale_document_attachments(self):
        for rec in self:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_id", "=", rec.id),
                    ("res_model", "=", self._name),
                    ("res_field", "=", "sale_document_attachment"),
                ]
            )
            if rec.sale_document_filename:
                attachment.name = rec.sale_document_filename
        return self.env["ir.attachment"].search(
            [
                ("res_id", "in", self.ids),
                ("res_model", "=", self._name),
                ("res_field", "=", "sale_document_attachment"),
            ]
        )
