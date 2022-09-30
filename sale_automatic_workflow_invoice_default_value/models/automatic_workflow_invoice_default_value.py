# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AutomaticWorkflowInvoiceDefaultValue(models.Model):

    _name = "automatic.workflow.invoice.default.value"
    _description = "Automatic Workflow Invoice Default Value"

    process_id = fields.Many2one(
        comodel_name="sale.workflow.process", required=True, ondelete="cascade"
    )

    invoice_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain="[('model', '=', 'account.move')]",
        required=True,
        ondelete="cascade",
    )
    value_type = fields.Selection(
        selection=[
            ("default_char_value", "Default Char Value"),
            ("from_sale_order", "From Sale Order"),
        ],
        required=True,
        default="default_char_value",
    )
    default_char_value = fields.Char()
    sale_order_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain="[('model', '=', 'sale.order')]",
        ondelete="cascade",
    )

    @api.constrains("invoice_field_id", "value_type", "sale_order_field_id")
    def _check_invoice_field_id(self):
        for record in self:
            invoice_field_type = record.invoice_field_id.ttype
            if record.value_type == "default_char_value":
                if invoice_field_type not in ["char", "text"]:
                    raise ValidationError(
                        _(
                            "With a default char value, the invoice field must"
                            " be of type char and not: {invoice_field_type}."
                        ).format(invoice_field_type=invoice_field_type)
                    )
            else:  # record.value_type == "from_sale_order"
                sale_order_field_type = record.sale_order_field_id.ttype
                if invoice_field_type != sale_order_field_type:
                    # Special case: char and text are considered identical
                    if invoice_field_type in [
                        "char",
                        "text",
                    ] and sale_order_field_type in ["char", "text"]:
                        continue
                    raise ValidationError(
                        _(
                            "With a from sale order value, the invoice field "
                            "type ({invoice_field_type}) must be the same type"
                            " than "
                            "the sale order field ({sale_order_field_type})."
                        ).format(
                            invoice_field_type=invoice_field_type,
                            sale_order_field_type=sale_order_field_type,
                        )
                    )
        return True

    @api.onchange("value_type")
    def _onchange_value_type(self):
        self.default_char_value = False
        self.sale_order_field_id = False
