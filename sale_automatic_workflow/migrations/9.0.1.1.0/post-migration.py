def migrate(cr, version=None):
    # set all default filters
    cr.execute(
        """
        with filters as (
            select substring(
                imd.name, length('automatic_workflow_') + 1
            ) as name,
            res_id, ir_filters.domain
            from ir_model_data imd
            join ir_filters on res_id=ir_filters.id
            where module='sale_automatic_workflow' and imd.name in (
                'automatic_workflow_order_filter',
                'automatic_workflow_picking_filter',
                'automatic_workflow_create_invoice_filter',
                'automatic_workflow_validate_invoice_filter',
                'automatic_workflow_sale_done_filter'
            )
        )
        update sale_workflow_process set
            create_invoice_filter_id=(
                select res_id from filters where name='create_invoice_filter'
            ),
            validate_invoice_filter_id=(
                select res_id from filters where name='validate_invoice_filter'
            ),
            order_filter_id=(
                select res_id from filters where name='order_filter'
            ),
            picking_filter_id=(
                select res_id from filters where name='picking_filter'
            ),
            sale_done_filter_id=(
                select res_id from filters where name='sale_done_filter'
            )
        """)
    # set flags depending on previous field
    cr.execute(
        """
        update sale_workflow_process set
            create_invoice=create_invoice_on <> 'manual'
        """
        )
