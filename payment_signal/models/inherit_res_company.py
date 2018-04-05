# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_signal = fields.Integer('Percent Signal in S.O.',
                                    default=20,
                                    store=True)

    @api.constrains('default_signal')
    @api.onchange('default_signal')
    def _check_signal(self):
        """Checking the values"""
        if not 0 <= self.default_signal <= 100:
            raise ValidationError(_("Error! The Percent Signal in S.O. "
                                    "can not be less than 0 "
                                    "nor more than 100."))
