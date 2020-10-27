# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_applicable_no_code_promo_program(self):
        programs = super()._get_applicable_no_code_promo_program()
        filtered_programs = self._filter_cumulative_programs(programs)
        filtered_programs = self._filter_pricelist_programs(filtered_programs)
        return self.env["sale.coupon.program"].browse(filtered_programs)

    def _filter_cumulative_programs(self, programs):
        # filter recordset of programs to cut non cumulative programs
        # method should respect the initial sequence of programs
        filtered_programs = []
        for program in programs:
            if not program.is_cumulative:
                filtered_programs.append(program.id)
            else:
                # when first non cumulative found cut the rest
                filtered_programs.append(program.id)
                break
        return filtered_programs

    def _filter_pricelist_programs(self, programs):
        return programs

    def _create_new_no_code_promo_reward_lines(self):
        super()._create_new_no_code_promo_reward_lines()

        program = self._get_applicable_no_code_promo_program().filtered(
            lambda p: p.reward_type == "use_pricelist"
        )
        if program and self.pricelist_id != program.reward_pricelist_id:
            self._update_pricelist(program.reward_pricelist_id)

    def _get_reward_line_values(self, program):
        # due to convention reward line should be created, in case of pricelist
        # we return an empty line with "Note" type
        if program.reward_type == "use_pricelist":
            # there always will be only one record but we need to send a list
            # cos implementation in code
            return [self._get_reward_values_pricelist(program)]
        return super()._get_reward_line_values(program)

    def _get_reward_values_pricelist(self, program):
        return {
            "name": _("Promotion Pricelist: ") + program.reward_pricelist_id.name,
            "display_type": "line_note",
            "sequence": 1000,
            "order_id": self.id,
            "is_reward_line": True,
            # because of implementation in core we need to send empty fields
            "product_id": False,
            "price_unit": False,
            "product_uom_qty": False,
            "product_uom": False,
        }

    def _update_existing_reward_lines(self):
        # case of updating lines for pricelist is not covered by base method
        # at this moment we updated order with up to date revard lines
        super()._update_existing_reward_lines()
        applied_programs = self._get_applied_programs_with_rewards_on_current_order()
        applied_programs = applied_programs.filtered(
            lambda p: p.reward_type == "use_pricelist"
        )
        for program in applied_programs:
            values = self._get_reward_line_values(program)
            # there always will be only one record
            values = values[0]
            if not [line for line in self.order_line if line.name == values["name"]]:
                self.write({"order_line": [(0, False, values)]})

    def _remove_invalid_reward_lines(self):
        super()._remove_invalid_reward_lines()
        new_sale_order = self.new({"partner_id": self.partner_id})
        new_sale_order.onchange_partner_id()
        self._update_pricelist(new_sale_order.pricelist_id)

    def _update_pricelist(self, pricelist):
        self.pricelist_id = pricelist
        for line in self.order_line:
            line.product_id_change()
