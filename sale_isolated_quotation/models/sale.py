# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_sequence = fields.Boolean(string="Order Sequence", readonly=True, index=True)
    quote_id = fields.Many2one(
        comodel_name="sale.order",
        string="Quotation",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="For Sales Order, this field references to its Quotation",
    )
    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Order",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="For Quotation, this field references to its Sales Order",
    )
    quotation_state = fields.Selection(
        string="Quotation Status",
        readonly=True,
        related="state",
        help="Only relative quotation states",
    )

    @api.model
    def is_using_quotation_number(self, vals):
        # By pass keep_name_so setting totally to keep it simple
        order_sequence = vals.get("order_sequence")
        order_sequence = order_sequence or self.env.context.get("order_sequence")
        return not order_sequence

    def _prepare_order_from_quotation(self):
        return {
            "name": self.env["ir.sequence"].next_by_code("sale.order") or "/",
            "order_sequence": True,
            "quote_id": self.id,
            "client_order_ref": self.client_order_ref,
        }

    def action_convert_to_order(self):
        self.ensure_one()
        if self.order_sequence:
            raise UserError(_("Only quotation can convert to order"))
        order = self.copy(self._prepare_order_from_quotation())
        self.order_id = order.id  # Reference from this quotation to order
        if self.state == "draft":
            self.action_done()
        return self.open_duplicated_sale_order()

    @api.model
    def open_duplicated_sale_order(self):
        return {
            "name": _("Sales Order"),
            "view_mode": "form",
            "view_id": False,
            "res_model": "sale.order",
            "context": {"default_order_sequence": True, "order_sequence": True},
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "domain": "[('order_sequence', '=', True)]",
            "res_id": self.order_id and self.order_id.id or False,
        }
