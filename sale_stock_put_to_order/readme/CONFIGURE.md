1.  Navigate to **Inventory ‣ Configuration ‣ Warehouses ‣ Locations**.
2.  Open (or create) the parent location that represents the
    put-to-order area (e.g. *PTO Zone*).
3.  Tick the **Is PTO** checkbox. All child locations inherit the flag.
4.  On the relevant **Operation Type** (e.g. *Receipts*), set the
    *Default Destination Location* to the PTO root.
5.  Optionally, go to **Inventory ‣ Configuration ‣ Settings** and
    enable **Auto-select PTO destination** under the *Put to Order*
    section. When enabled, the system automatically assigns the proposed
    PTO bin as the destination on move lines during reservation
    (`action_assign`). When disabled, the destination is only proposed
    and must be applied manually.
