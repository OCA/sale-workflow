The endpoint requires the partner ID of the customer prices for which you want to retrieve prices.
It should be called like this::

    curl -X GET "http://your.odoo/pricelist/$partner_id" -H "accept: /" -H "API-KEY: XYZ"

By default you'll get a list of dict like this::

    [
        {"id": $product_id, "price": $price},
        {"id": $product_id, "price": $price},
        {"id": $product_id, "price": $price},
    ]

You can modify the `ir.exports` configuration named "Pricelist Cache Parser" to change this schema.
