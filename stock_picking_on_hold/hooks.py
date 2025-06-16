# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    """Remove payment_method_id field references when module is uninstalled."""
    _logger.info("Running uninstall hook for stock_picking_on_hold")
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        try:
            # Remove any stored search filters that reference payment_method_id
            filters = env['ir.filters'].search([
                ('model_id', '=', 'sale.order'),
                ('domain', 'ilike', 'payment_method_id')
            ])
            if filters:
                _logger.info("Removing %d filters referencing payment_method_id", len(filters))
                filters.unlink()
            
            # Remove any stored user preferences/contexts that reference the field
            user_contexts = env['ir.default'].search([
                ('field_id.model_id.model', '=', 'sale.order'),
                ('field_id.name', '=', 'payment_method_id')
            ])
            if user_contexts:
                _logger.info("Removing %d user contexts referencing payment_method_id", len(user_contexts))
                user_contexts.unlink()
            
            # Clean up any view customizations that might reference the field
            view_customizations = env['ir.ui.view.custom'].search([
                ('arch', 'ilike', 'payment_method_id')
            ])
            if view_customizations:
                _logger.info("Removing %d view customizations referencing payment_method_id", len(view_customizations))
                view_customizations.unlink()
            
            # Clear any saved list views or form views that include the field
            # This is often the cause of the "Invalid field" error
            cr.execute("""
                DELETE FROM ir_ui_view_custom 
                WHERE arch LIKE '%payment_method_id%'
            """)
            
            # Clear any stored search contexts
            cr.execute("""
                DELETE FROM ir_filters 
                WHERE model_id = 'sale.order' 
                AND domain LIKE '%payment_method_id%'
            """)
            
            _logger.info("Successfully cleaned up payment_method_id field references")
            
        except Exception as e:
            _logger.error("Error during uninstall hook: %s", str(e))
            # Don't raise the exception to avoid blocking uninstall
