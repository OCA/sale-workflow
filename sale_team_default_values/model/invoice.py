# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Author: Guewen Baconnier, Leonardo Pistone
# Copyright 2014-2015 Camptocamp SA

from openerp import models, api


class Invoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('section_id')
    def onchange_section_id(self):
        if self.section_id and self.section_id.journal_id:
            self.journal_id = self.section_id.journal_id
