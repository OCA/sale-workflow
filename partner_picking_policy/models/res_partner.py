# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_selection_picking_policy(self):
        """
        Get all possible selection choice for picking_policy
        (based on the same field on sale.order).
        :return: list of tuple (str, str)
        """
        target_field = "picking_policy"
        fields_get = self.env['sale.order'].fields_get(
            allfields=[target_field])
        return [(v[0], _(v[1])) for v in fields_get[target_field]['selection']]

    picking_policy = fields.Selection(
        selection="_get_selection_picking_policy",
        help="Select a specific picking policy for this customer.\n"
             "You can let the global picking policy by "
             "letting emtpy this field.",
        default="",
    )
