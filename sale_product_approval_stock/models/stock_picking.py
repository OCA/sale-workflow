# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    do_exceptions = fields.Boolean(
        compute="_compute_stock_exception", string="Stock Exception"
    )
    override_exception = fields.Boolean("Override Exception", default=False)

    @api.depends("move_ids_without_package.do_line_exceptions")
    def _compute_stock_exception(self):
        for rec in self:
            rec.do_exceptions = any(
                not line.do_line_exceptions for line in rec.move_ids_without_package
            )

    def _log_exception_activity_stock(self, product_id):
        for order in self:
            note = self._render_product_state_excep(order, product_id)
            order.activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=order.user_id.id or SUPERUSER_ID,
            )

    def _render_product_state_excep(self, order, product_id):
        values = {"delivery_order_ref": order, "product_ref": product_id}
        return self.env.ref(
            "sale_product_approval_stock.exception_on_delivery_order"
        )._render(values=values)

    def button_validate(self):
        res = super().button_validate()
        self.check_do_exception()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        self.check_do_exception()
        return res

    def check_do_exception(self):
        for do in self:
            if (
                do.do_exceptions
                and not do.override_exception
                and not self._context.get("override_ex")
            ):
                raise UserError(
                    _(
                        "You can not do Validate/Mark as Done because some products are not "
                        "allowed in this delivery order."
                    )
                )
        return True


class StockMove(models.Model):
    _inherit = "stock.move"

    do_line_exceptions = fields.Boolean(related="product_id.ship_ok")
    pick_state = fields.Selection(related="picking_id.state", string="Picking State")
