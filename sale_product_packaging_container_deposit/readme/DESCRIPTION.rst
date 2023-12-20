This module allows you to add product packaging to an order automatically.
Based on the order line quantity with associated packaging, the quantity of product packaging is calculated and added to the order. 

Hypothesis:

* package type "Pack of 12" has the container deposit "pack of 12"
* package type "Pack of 24" has the container deposit "pack of 24"
* package type "EUROPAL" has the container deposit "EU pallet"


.. list-table:: Product A has those packaging:
    :widths: 50 50 25
    :header-rows: 1

    * - package type
      - package level
      - qty
    * - Pack of 12
      - PACK
      - 12
    * - Pack of 24
      - Pack
      - 24
    * - EUROPAL
      - PALLET
      - 240

Order Line:

* Case 1: Product A | qty = 280. Result:

  * 280 // 240 = 1 => add order line for 1 EU pallet
  * 280 // 24 (biggest PACK) => add SO line for 11 pack of 24
* Case 2: Product A | qty = 280 and packaging=Pack of 12. Result:

  * 280 // 240 =1 => add order line for 1 EU pallet
  * 280 // 12 (forced packaging for PACK) => add order line for 23 pack of 12
* Case 3: Product A &  Product B. Both have a deposit of 1 pack of 24 

  * only one line for 2 pack of 24
