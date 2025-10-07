# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commitment_date = fields.Datetime(
        "Delivery Date",
        compute="_compute_commitment_date",
        store=True,
        readonly=False,
        recursive=True,
        copy=False,
    )

    @api.depends("linked_line_id", "linked_line_id.commitment_date")
    def _compute_commitment_date(self):
        for record in self:
            combo_line = record.linked_line_id
            if combo_line:
                record.commitment_date = combo_line.commitment_date

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()  # has ensure_one already
        com_date = self.commitment_date
        if com_date:
            vals.update(
                date_planned=com_date
                - timedelta(days=self.order_id.company_id.security_lead),
                date_deadline=com_date,
            )
        return vals

    def write(self, vals):
        # Propagate a new commitment date to pending stock moves
        res = super().write(vals)
        if "commitment_date" in vals:
            commitment_date = vals.get("commitment_date")
            if commitment_date:
                self._propagate_date_deadline_to_moves(commitment_date)
            else:
                for line in self:
                    date = line.order_id.commitment_date or line._expected_date()
                    line._propagate_date_deadline_to_moves(date)
        return res

    def _propagate_date_deadline_to_moves(self, date):
        moves_todo = self.move_ids.filtered(
            lambda sm: sm.state not in ["cancel", "done"]
        )
        move_values = {
            "date_deadline": date,
        }
        moves_todo.write(move_values)
