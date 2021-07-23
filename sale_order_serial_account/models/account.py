# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    line_serial_list = fields.Text(
        string="Serial List", related="invoice_line_ids.serial_list"
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    serial_list = fields.Text(string="Serial List", copy=False)
