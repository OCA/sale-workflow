# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_applicable_no_code_promo_program(self):
        # filter recordset of programs to cut non cumulative programs
        # method should respect the initial sequence of programs
        programs = super()._get_applicable_no_code_promo_program()
        filtered_programs = []
        for program in programs:
            if not program.is_cumulative:
                filtered_programs.append(program.id)
            else:
                # when first non cumulative found cut the rest
                filtered_programs.append(program.id)
                break
        return self.env["sale.coupon.program"].browse(filtered_programs)
