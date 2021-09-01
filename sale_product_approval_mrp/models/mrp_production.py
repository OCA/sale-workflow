# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    mo_exceptions = fields.Boolean(
        related="product_id.mrp_ok",
        string="MO Exceptions",
        default=True,
    )
    bom_mo_exception = fields.Boolean(
        compute="_compute_bom_exception", string="BoM Exception"
    )
    mo_line_exceptions = fields.Boolean(
        compute="_compute_mo_exceptions", string="MO Line Exceptions"
    )
    override_exception = fields.Boolean("Override Exception", default=False)

    @api.depends("move_raw_ids.approved_mrp_component_ok")
    def _compute_mo_exceptions(self):
        for rec in self:
            rec.mo_line_exceptions = any(
                not line.approved_mrp_component_ok for line in rec.move_raw_ids
            )

    @api.depends("bom_id")
    def _compute_bom_exception(self):
        for rec in self:
            rec.bom_mo_exception = (
                True
                if (rec.bom_id.bom_line_exceptions or rec.bom_id.bom_exceptions)
                else False
            )

    def _log_exception_activity_mrp(self, product_id):
        for order in self:
            note = self._render_product_state_excep(order, product_id)
            order.activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=order.user_id.id or SUPERUSER_ID,
            )

    def _render_product_state_excep(self, order, product_id):
        values = {"mrp_order_ref": order, "product_ref": product_id}
        return self.env.ref(
            "sale_product_approval_mrp.exception_on_mrp_production"
        )._render(values=values)

    def action_confirm(self):
        res = super(MRPProduction, self).action_confirm()
        for mo in self:
            if (
                (mo.mo_line_exceptions or mo.bom_mo_exception)
                and not mo.override_exception
                and not self._context.get("override_ex")
            ):
                raise UserError(
                    _(
                        "You can not confirm this manufacturing order "
                        "because some products are not allowed in this order."
                    )
                )
        return res

    def button_mark_done(self):
        res = super(MRPProduction, self).button_mark_done()
        for mo in self:
            if (
                mo.mo_line_exceptions or mo.bom_mo_exception
            ) and not mo.override_exception:
                raise UserError(
                    _(
                        "You can not mark done because some products are not "
                        "allowed in this order."
                    )
                )
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    approved_mrp_component_ok = fields.Boolean(related="product_id.mrp_component_ok")
    mrp_order_state = fields.Selection(
        related="raw_material_production_id.state", string="MRP Order State"
    )
