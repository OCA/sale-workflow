from odoo import models


class ProductSetAdd(models.TransientModel):
    _inherit = "product.set.add"

    def prepare_sale_order_line_data(self, set_line, max_sequence=0):
        """
        Adds specific sections data to lines
        """
        sol_data = super().prepare_sale_order_line_data(set_line, max_sequence)

        if set_line.display_type:
            sol_data.update(
                {"name": set_line.name, "display_type": set_line.display_type}
            )
        return sol_data
