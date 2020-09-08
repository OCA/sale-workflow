# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_need_po = fields.Boolean(
        string='Customer Requires PO', track_visibility="onchange",
    )
    sale_doc = fields.Text(
        string='Sales Require Documentation', track_visibility="onchange",
    )
