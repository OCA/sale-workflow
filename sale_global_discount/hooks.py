from odoo.tools.sql import column_exists


def _pre_init_global_discount_fields(cr):
    if not column_exists(cr, "sale_order", "amount_global_discount"):
        cr.execute(
            """
                ALTER TABLE "sale_order"
                ADD COLUMN "amount_global_discount" double precision DEFAULT 0
            """
        )
        cr.execute(
            """
        ALTER TABLE "sale_order" ALTER COLUMN "amount_global_discount" DROP DEFAULT
        """
        )
    if not column_exists(cr, "sale_order", "amount_untaxed_before_global_discounts"):
        cr.execute(
            """
                ALTER TABLE "sale_order"
                ADD COLUMN "amount_untaxed_before_global_discounts" double precision
            """
        )
        cr.execute(
            """
        update sale_order set amount_untaxed_before_global_discounts = amount_untaxed
        """
        )
    if not column_exists(cr, "sale_order", "amount_total_before_global_discounts"):
        cr.execute(
            """
                ALTER TABLE "sale_order"
                ADD COLUMN "amount_total_before_global_discounts" double precision
            """
        )
        cr.execute(
            """
        update sale_order set amount_total_before_global_discounts = amount_total
        """
        )
