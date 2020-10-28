# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def add_reward_line_values(self, program):
        """Add the rewarded product if a reward line has been found for this
        product
        """
        reward_product = program.reward_product_id
        taxes = reward_product.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        sequence = (max(self.mapped("order_line.sequence"))) + 1
        sol = self.order_line.create(
            {
                "sequence": sequence,
                "name": reward_product.name,
                "product_id": reward_product.id,
                "price_unit": reward_product.lst_price,
                "is_reward_line": False,
                "forced_reward_line": True,
                "product_uom_qty": program.reward_product_quantity,
                "product_uom": reward_product.uom_id.id,
                "tax_id": [(4, tax.id, False) for tax in taxes],
                "order_id": self.id,
            }
        )
        sol.product_id_change()
        return sol

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
        # TODO: rollback forced lines which is not used for creation of
        # reward lines for other programs
        super()._remove_invalid_reward_lines()
        new_sale_order = self.new({"partner_id": self.partner_id})
        new_sale_order.onchange_partner_id()
        self._update_pricelist(new_sale_order.pricelist_id)

    def _update_pricelist(self, pricelist):
        self.pricelist_id = pricelist
        for line in self.order_line:
            line.product_id_change()

    # FIXME: find simpler solution, so write/unlink would not
    # be so complicating when handling related discount line removal.
    def write(self, vals):
        """Override to clean up order lines.

        If line unlink is triggered via write, same functionality is
        triggered as via unlink, to mark related discount line for
        removal. Context `discount_data_removed` is passed to not try
        removing same lines via sale.order.line unlink.
        """

        def get_unlink_order_lines(order_lines_data):
            line_ids = [i[1] for i in order_lines_data if i[0] == 2]
            return SaleOrderLine.browse(line_ids)

        def clean_lines(lines, order_line_ids):
            new_lines = []
            for line_data in lines:
                new_line_data = line_data
                code = line_data[0]
                if code in (1, 3, 4) and line_data[1] in order_line_ids:
                    new_line_data = (2, line_data[1], 0)
                elif code == 6:
                    # NOTE. No need to specify new_line_data here,
                    # because code 6 will only keep specified IDs
                    # anyway.
                    line_ids = line_data[2]
                    for line_id in order_line_ids:
                        if line_id in line_ids:
                            line_ids.remove(line_id)
                new_lines.append(new_line_data)
            return new_lines

        if vals.get("order_line"):
            SaleOrderLine = lines_to_remove = self.env["sale.order.line"]
            unlink_order_lines = get_unlink_order_lines(vals["order_line"])
            lines_to_remove = (
                unlink_order_lines._collect_discount_lines_and_remove_programs()
            )
            if lines_to_remove:
                vals["order_line"] = clean_lines(
                    vals["order_line"], lines_to_remove.ids
                )
                self = self.with_context(discount_data_removed=True)
        return super(SaleOrder, self).write(vals)

    def first_order(self):
        """Check if this is first partner order.

        Returns:
            True if there are no other non-cancelled orders for this
            commercial partner, False otherwise.

        """
        self.ensure_one()
        partner_id = self.partner_id.commercial_partner_id.id
        domain = [
            ("partner_id.commercial_partner_id", "=", partner_id),
            ("state", "!=", "cancel"),
        ]
        # Lets check promotions on virtual sale order.
        if not isinstance(self.id, models.NewId):
            domain.append(("id", "!=", self.id))
        return not self.search_count(domain)
