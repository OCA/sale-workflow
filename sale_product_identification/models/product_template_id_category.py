# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import inspect

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval, test_python_expr


def _contains_expression(code):
    """Return True when the string contains any non-comment expression."""
    for line in (code or "").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


class ProductTemplateIdcategory(models.Model):
    _name = "product.template.id_category"
    _description = "Product Template Identification Category"

    product_tmpl_id = fields.Many2one("product.template")
    category_id = fields.Many2one("res.partner.id_category")
    is_mandatory = fields.Boolean(
        default=True, help="Defines whether identification is mandatory."
    )
    message = fields.Text(
        help="Allows you to define a description of why "
        "this identification is being added.\n"
        "Example: Asking the customer for identification"
    )
    value = fields.Text(
        string="Extra validation",
        help="Define the Python expression to perform an extra check. "
        "Leave this field blank if you do not want this check. "
        "Note that it will always be evaluated.",
    )

    def _default_eval_context(self):
        return self.env._(
            """# Extra validation executed during identification checks.
              # Leave this field empty or commented to skip the extra validation.
              # Available variables:
              # env: environment on which the action is triggered
              # order: Current record of the sale.order
              # time, datetime, dateutil, timezone: useful Python libraries
              # float_compare: utility function to compare
              #                floats based on specific precision
              # result (bool): Set to True to approve the validation,
              #                keep False to fail it.
              # Example:
              # result = order.amount_total < 500.0  # approve only when
              #                                      # amount is below 500
          """
        )

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["value"] = self._default_eval_context()
        return defaults

    def _get_eval_context(self, eval_context=None):
        return {
            "env": self.env,
            "order": None,
            # tools
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "float_compare": float_compare,
            "result": False,
        } | (eval_context or {})

    def _test_python_expr(self):
        """
        Test the Python expression syntax.
        """
        if self.value:
            message_error = test_python_expr(expr=self.value, mode="exec")
            if message_error:
                raise ValidationError(str(message_error))
        return True

    def _normalize_value(self, value=None):
        format_value = value or self.value or ""
        format_value = format_value.replace("\r\n", "\n")
        format_value = format_value.expandtabs(4)
        return inspect.cleandoc(format_value).strip()

    @api.onchange("value")
    def _onchange_value(self):
        for prod_category in self:
            prod_category._normalize_value()

    @api.constrains("value")
    def _check_value(self):
        for prod_category in self:
            if prod_category.value:
                prod_category._test_python_expr()

    def _eval_value(self, record):
        self.ensure_one()
        if self.value:
            if not _contains_expression(self.value):
                return True
            message_error = self.env._(
                "An error occurred while evaluating "
                "the expression for product %(product)s and "
                "identification category %(category)s: \n\n"
            ) % {
                "product": self.product_tmpl_id.name,
                "category": self.category_id.name,
            }
            try:
                context = self._get_eval_context(
                    eval_context={
                        "order": record,
                    }
                )
                safe_eval(
                    self.value,
                    context,
                    mode="exec",
                    nocopy=True,
                )
                return context.get("result", False)
            except Exception as ex:
                raise ValidationError(message_error + str(ex).split("\n")[0]) from ex
        return True
