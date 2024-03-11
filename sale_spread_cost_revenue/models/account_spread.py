# Copyright 2024 Ecosoft (<https://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountSpread(models.Model):
    _inherit = "account.spread"

    sale_line_id = fields.Many2one(
        "sale.order.line",
        string="Sales order line",
    )
    sale_id = fields.Many2one(
        related="sale_line_id.order_id",
        readonly=True,
        store=True,
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("sale_line_id"):
            sline = self.env["sale.order.line"].browse(vals["sale_line_id"])
            sline.write({"spread_id": res.id})
        return res

    @api.depends(
        "estimated_amount",
        "currency_id",
        "company_id",
        "invoice_line_id.price_subtotal",
        "invoice_line_id.currency_id",
        "sale_line_id.price_subtotal",
        "sale_line_id.currency_id",
        "line_ids.amount",
        "line_ids.move_id.state",
    )
    def _compute_amounts(self):
        for spread in self:
            if spread.sale_line_id:
                spread.estimated_amount = -spread.sale_line_id.price_subtotal
        res = super()._compute_amounts()
        return res

    def action_unlink_sale_line(self):
        """Unlink the sale line from the spread board"""
        self.ensure_one()
        if self.sale_id.state != "draft":
            msg = _("Cannot unlink sales lines if the sales order is validated")
            raise UserError(msg)
        self._action_unlink_sale_line()

    def _action_unlink_sale_line(self):
        self._message_post_unlink_sale_line()
        self.sale_line_id.spread_id = False
        self.sale_line_id = False

    def _message_post_unlink_sale_line(self):
        for spread in self:
            sale_link = (
                "<a href=# data-oe-model=account.move "
                "data-oe-id=%d>%s</a>" % (spread.sale_id.id, _("Sales Order"))
            )
            msg_body = _(
                "Unlinked invoice line '%(spread_line_name)s' (view %(sale_link)s)."
            ) % {
                "spread_line_name": spread.sale_line_id.name,
                "sale_link": sale_link,
            }
            spread.message_post(body=msg_body)
            spread_link = (
                "<a href=# data-oe-model=account.spread "
                "data-oe-id=%d>%s</a>" % (spread.id, _("Spread"))
            )
            msg_body = _("Unlinked '%(spread_link)s' (sales line %(sale_line)s).") % {
                "spread_link": spread_link,
                "sale_line": spread.sale_line_id.name,
            }
            spread.sale_id.message_post(body=msg_body)

    def _compute_spread_board(self):
        self.ensure_one()
        if self.invoice_line_id.spread_on_sale:
            return
        super()._compute_spread_board()
