Known Limitations:

- Kit component customization and delivered quantity computation currently apply to single-level phantom BoMs.
- Multi-level phantom BoM delivered quantity computation is not currently supported. If a kit component has its own phantom BoM, downstream stock moves are created for the sub-kit components and do not match the parent kit component line, resulting in a delivered quantity computation of 0.0.
