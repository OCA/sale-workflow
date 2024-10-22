# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Quentin DUPONT (https://twitter.com/pondupont)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrderDuplicationWizard(models.TransientModel):
    _name = "sale.order.duplication.wizard"
    _description = "Sale Order Duplication Wizard"

    _DUPLICATION_TYPE_KEYS = [
        ("week", "Weekly"),
        ("month", "Monthly"),
    ]

    # Column Section
    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        readonly=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=True,
    )

    begin_date = fields.Date(
        required=True,
    )

    include_current_date = fields.Boolean(default=False)

    duplication_type = fields.Selection(
        selection=_DUPLICATION_TYPE_KEYS,
        default="week",
        required=True,
    )

    duplication_duration = fields.Integer(required=True, default=0)

    date_line_ids = fields.One2many(
        comodel_name="sale.order.duplication.wizard.date.line",
        inverse_name="wizard_id",
        string="New Dates",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get("active_id", False)
        if not order_id:
            res.update({"order_id": False})
            res.update({"partner_id": False})
            res.update({"begin_date": False})
        else:
            order = self.env["sale.order"].browse(order_id)
            res.update({"order_id": order_id})
            res.update({"partner_id": order.partner_id.id})
            res.update({"begin_date": order.date_order.strftime("%Y-%m-%d")})

        return res

    # View Section
    @api.onchange(
        "begin_date", "duplication_type", "duplication_duration", "include_current_date"
    )
    def onchange_duplication_settings(self):
        self.ensure_one()
        self.date_line_ids = []

        if self.begin_date and self.duplication_type and self.duplication_duration:
            date_line_ids = []
            date_line_ids.append((5, 0, 0))
            begin_index = 0
            end_index = self.duplication_duration
            if not self.include_current_date:
                begin_index += 1
                end_index += 1
            for i in range(begin_index, end_index):
                if self.duplication_type == "week":
                    current_date = self.begin_date + datetime.timedelta(weeks=i)
                else:
                    current_date = self.begin_date + relativedelta(months=i)
                date_line_ids.append(
                    (
                        0,
                        0,
                        {
                            "commitment_date": current_date.strftime("%Y-%m-%d"),
                        },
                    )
                )
            self.date_line_ids = date_line_ids

    def duplicate_button(self):
        self._duplicate()
        return True

    def duplicate_open_button(self):
        order_ids = self._duplicate()
        action_name = "sale.action_quotations"
        action = self.env["ir.actions.act_window"]._for_xml_id(action_name)
        action["domain"] = "[('id', 'in', [" + ",".join(map(str, order_ids)) + "])]"
        return action

    def _duplicate(self):
        self.ensure_one()
        order_ids = []
        for date_line in self.date_line_ids:
            order_ids.append(
                self.order_id.copy(
                    default={
                        "commitment_date": date_line.commitment_date,
                        "date_order": date_line.commitment_date,
                    }
                ).id
            )
        return order_ids
