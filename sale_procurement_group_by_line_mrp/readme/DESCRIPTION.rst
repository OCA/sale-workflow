This is a glue module that fixes a double procurement bug when both
``sale_procurement_group_by_line`` and ``sale_mrp`` are installed together.
It installs automatically when both modules are present.

``sale_mrp`` overrides ``_get_qty_procurement`` for kit products and ignores
``previous_product_uom_qty``, using ``_compute_kit_quantities()`` instead.
For nested kits, the inner kit's component moves don't match the outer kit's
BoM, so it returns 0, causing ``super()._action_launch_stock_rule`` to run
procurement a second time and double all stock moves.

By checking ``previous_product_uom_qty`` first (only for kit products),
we signal that procurement was already handled upstream, without affecting
the default behavior for non-kit products.
