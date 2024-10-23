# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, exceptions, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_project_ids(self):
        """
        Override related projects computation to
        include projects containing tasks related to
        order lines of this quotation
        """
        super()._compute_project_ids()
        quotation_projects = self.env["project.project"].search(
            [
                ("quotation_id", "in", self.ids),
            ]
        )
        for order in self:
            order_projects = quotation_projects.filtered(
                lambda p: p.quotation_id.id == order.id
            )
            order.project_ids |= order_projects
            order.project_count = len(order.project_ids)
        return

    def _compute_tasks_ids(self):
        """
        Override related tasks computation to
        include tasks related to order lines
        of this quotation
        """
        super()._compute_tasks_ids()
        quotation_lines_ids = self.mapped("order_line").ids
        quotation_tasks = self.env["project.task"].search(
            [
                ("quotation_line_id", "in", quotation_lines_ids),
            ]
        )
        for order in self:
            order_tasks = quotation_tasks.filtered(
                lambda t: t.quotation_line_id.id in order.order_line.ids
            )
            order.tasks_ids |= order_tasks
            order.tasks_count = len(order.tasks_ids)
        return

    @api.model
    def _prepare_task_vals(
        self,
        project,
        order_line,
    ):
        """
        Prepare vals for task creation

        Args:
        project (project.project): Project
        order_line (sale.order.line): Order line

        Returns:
            dict: Dictionary of task values
        """
        return {
            "name": order_line.name,
            "project_id": project.id,
            "quotation_line_id": order_line.id,
            "active": True,
        }

    @api.model
    def _prepare_project_vals(self, sale_order):
        """
        Prepare vals for project creation

        Args:
        sale_order (sale.order): Sale Order

        Returns:
            dict: Dictionary of project values
        """
        return {
            "name": sale_order.name,
            "quotation_id": sale_order.id,
            "active": True,
        }

    @api.model
    def _get_quotation_project_template(self):
        """
        Method to obtain a template for quotation project
        from settings. If not set or is invalid, logs a warning

        Returns:
            project.project record or None
        """
        try:
            return self.env["project.project"].browse(
                int(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("project_from_quotation.template_project_id")
                )
            )
        except ValueError:
            _logger.warning(
                "Project template ID is not set or invalid. "
                "Make sure you have configured it in settings."
            )

    @api.model
    def _get_quotation_task_template(self):
        """
        Method to obtain a template for quotation task
        from settings. If not set or is invalid, logs a warning

        Returns:
            project.task record or None
        """
        try:
            return self.env["project.task"].browse(
                int(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("project_from_quotation.template_task_id")
                )
            )
        except ValueError:
            _logger.warning(
                "Task template ID is invalid or not set. "
                "Make sure you have configured it in settings."
            )

    def _get_order_lines_unique_products(self, order_lines):
        """
        Get order lines with unique products

        Args:
            order_lines (sale.order.line recordset): Order lines
            if not set, uses self.order_line

        Returns:
            sale.order.line recordset: Every first
            line with the same product
        """
        self.ensure_one()
        unique_products = []
        res_order_lines = self.env["sale.order.line"]
        order_lines = order_lines.filtered("product_id")

        for line in order_lines:
            if line.product_id.id not in unique_products:
                unique_products.append(line.product_id.id)
                res_order_lines |= line

        return res_order_lines

    def _create_project_from_quotation(
        self,
        order_lines,
        mode="project",
    ):
        """
        Create project from a quotation

        Args:
        order_lines (sale.order.line): Order lines to use for tasks creation
        mode (str): Project creation mode. Possible values:
            project - create a new empty project
            tasks_per_line - create a project with tasks for each order line
            tasks_per_product - create a project with tasks for each product

        Returns:
            Created record of the project.project model
        """
        self.ensure_one()
        project = False
        task_obj = self.env["project.task"]
        project_obj = self.env["project.project"]
        order_lines = order_lines.filtered(lambda x: not x.task_id)
        task_vals = {}
        project_template = self._get_quotation_project_template()
        if project_template:
            project = project_template.copy(self._prepare_project_vals(self))
        else:
            project = project_obj.create(self._prepare_project_vals(self))

        if mode in ["tasks_per_line", "tasks_per_product"]:
            tasks = self.env["project.task"]
            if mode == "tasks_per_line":
                task_vals = [
                    self._prepare_task_vals(project, line) for line in order_lines
                ]
            elif mode == "tasks_per_product":
                task_vals = [
                    self._prepare_task_vals(project, line)
                    for line in self._get_order_lines_unique_products(order_lines)
                ]
            template_task = self._get_quotation_task_template()
            if template_task:
                for vals in task_vals:
                    tasks |= template_task.copy(vals)
            else:
                tasks = task_obj.create(task_vals)

        return project

    def create_project_from_quotation(self):
        """
        Method to call action window for wizard (project.from.quotation)
        Returns:
            dict: Action window
        """
        if len(self) > 1:
            raise exceptions.UserError(
                _("You can create project only from one quotation at a time!")
            )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "project_from_quotation.project_from_quotation_action"
        )
        action["context"] = {"default_sale_order_id": self.id}
        return action

    def action_view_task(self):
        """
        Override action opening tasks to
        remove default searching by sale order
        """
        action = super().action_view_task()
        if "search_default_sale_order_id" in action["context"]:
            del action["context"]["search_default_sale_order_id"]
        return action
