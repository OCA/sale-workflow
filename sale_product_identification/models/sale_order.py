# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _diff_identification(self, compare_identification_ids):
        diff_identification = self.env["res.partner.id_number"].validate_identification(
            **{
                "compare_identification_ids": compare_identification_ids,
                "partner_id": self.partner_id.id,
            }
        )
        return diff_identification

    def _message_error_identifications(self, diff_identification=False, required=False):
        """
        Display messages created using the message_error_identifications
        method in order of sale.

        :param diff_identification: Required or optional identifications.
        :return: Message by order
        """
        message_error = ""
        for order in self:
            message_error = _("%(order)s%(message)s") % {
                "order": f"\n{order.name}" if len(self) > 1 else "",
                "message": self.env[
                    "res.partner.id_number"
                ].message_error_identifications(
                    order.mapped("order_line.product_template_id").filtered(
                        lambda product: product.required_identification
                        and product.product_tmpl_category_ids
                    ),
                    diff_identification,
                    required,
                ),
            }

        return message_error

    def _action_generate_confirm_identification(self, message):
        view = self.env.ref("sale_product_identification.confirm_identification_view")
        return {
            "name": _("Confirm identification"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "confirm.identification",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": {
                "default_order_ids": [Command.set(self.ids)],
                "default_message": message,
            },
        }

    def _get_domain_identifications(self, is_mandatory=False):
        return [
            ("product_tmpl_id", "in", self.order_line.product_template_id.ids),
            ("product_tmpl_id.required_identification", "=", True),
            ("is_mandatory", "=", is_mandatory),
        ]

    def _validate_opt_identification(self):
        self.ensure_one()
        products_opt_identification_ids = (
            self.env["product.template.id_category"]
            .search(self._get_domain_identifications())
            .mapped("category_id")
        )
        if products_opt_identification_ids:
            message = _(
                "The following identifications require verification, "
                "please validate before continuing:\n %(identifications)s"
            ) % {
                "identifications": self._message_error_identifications(
                    products_opt_identification_ids.ids
                )
            }
            return self._action_generate_confirm_identification(message)
        return True

    def _validate_identification(self):
        self.ensure_one()
        products_identification_ids = (
            self.env["product.template.id_category"]
            .search(self._get_domain_identifications(True))
            .mapped("category_id")
        )
        if products_identification_ids:
            diff_identification = self._diff_identification(products_identification_ids)
            if diff_identification:
                message = _(
                    "The following identifications are required for "
                    "partner, please verify.\n %(identifications)s"
                ) % {
                    "identifications": self._message_error_identifications(
                        diff_identification.ids, True
                    )
                }
                raise ValidationError(message)

    def action_confirm(self):
        for order in self:
            order._validate_identification()
        if not self.env.context.get("not_verify_optional_identification", False):
            res = self[:1]._validate_opt_identification()
            if res is not True:
                return res
        return super().action_confirm()
