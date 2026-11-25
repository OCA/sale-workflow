import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """
    Pre-initialize forecast fields with default values (all available).
    """
    _logger.info("Pre-initializing forecast availability fields...")
    if not column_exists(env.cr, "sale_order_line", "forecasted_issue"):
        _logger.info("Adding forecasted_issue column to sale_order_line...")
        create_column(env.cr, "sale_order_line", "forecasted_issue", "boolean")
        env.cr.execute("""
            UPDATE sale_order_line
            SET forecasted_issue = FALSE
        """)
        _logger.info("Set all order lines to no forecast issues (default).")
    if not column_exists(env.cr, "sale_order", "sale_forecast_available"):
        _logger.info("Adding sale_forecast_available column to sale_order...")
        create_column(env.cr, "sale_order", "sale_forecast_available", "boolean")
        env.cr.execute("""
            UPDATE sale_order
            SET sale_forecast_available = TRUE
        """)
        _logger.info("Set all orders as forecast available (default).")
    _logger.info("Pre-initialization complete!")


def post_init_hook(env):
    """
    Compute actual forecast values for active orders using ORM.
    Completed/cancelled orders keep their default values (available).
    """
    _logger.info("Computing forecast values for active orders...")
    active_orders = env["sale.order"].search(
        [("state", "!=", "cancel"), ("delivery_status", "!=", "full")]
    )
    active_orders.mapped("order_line")._compute_forecasted_issue()
    active_orders._compute_sale_forecast_available()
    _logger.info("Post-initialization complete!")
