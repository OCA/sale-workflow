This module extends the functionality of the standard ``sale_blanket_order``
module with advanced features for managing complex blanket order scenarios.

**Features:**

* **Version Management**: Create and track multiple versions of a blanket order
* **Order Plan Management**: Plan and generate sale orders through installments
* **Cost Tracking**: Monitor product and service costs against targets

**New Models:**

* ``blanket.order.plan`` - Order plan for installment management
* ``blanket.order.product`` - Product cost tracking
* ``blanket.order.service`` - Service cost tracking

**Dependencies:**

* ``sale_blanket_order`` - Base module for blanket orders (OCA)
* ``base_revision`` - For version tracking functionality (OCA)