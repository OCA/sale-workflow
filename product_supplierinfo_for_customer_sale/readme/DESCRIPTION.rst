Based on product_supplierinfo_for_customer, this module loads in every sale order the
customer code defined in the product and allows
use the product codes and product name configured in each products in sale
orders.

To use this module, you need:

- Go to product and configure *Partner product name* and *Partner product code*
  for each selected customer.

.. figure:: static/description/configuration_customer.png
    :alt: Configure customer codes
    :width: 600 px

- When add order lines in sale quotation for a customer that has an specific
  name and code in the product, you can search that product with that customer
  name or code. Then, this values will be displayed in product description.

.. figure:: static/description/search_code.png
    :alt: Search by exist customer code
    :width: 600 px

.. figure:: static/description/description_code.png
    :alt: Search by exist customer code
    :width: 600 px

- If product does not have a configuration for customer selected, product will
  be search by its default code.

.. figure:: static/description/search_code_2.png
    :alt: Search by exist customer code
    :width: 600 px

.. figure:: static/description/description_code_2.png
    :alt: Search by exist customer code
    :width: 600 px
