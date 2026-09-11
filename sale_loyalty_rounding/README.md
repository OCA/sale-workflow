# instance_creator — Instance Creator

> **Version:** 19.0.1.0.0 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

`instance_creator` is the main installer/meta-module for the Promovago project. It serves as the entry point application that declares the top-level dependency chain for a Promovago Odoo instance. The module does not define custom models, views, or business logic of its own; its purpose is to aggregate and enforce the correct set of module dependencies for the deployment.

## Dependencies

### Odoo / OCA Modules

- `l10n_mx` — Mexico localization module; provides the Mexican chart of accounts, fiscal positions, tax configurations, and other MX-specific accounting structures required by the Promovago instance.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `Instance Creator` and click **Install**.
4. Odoo will automatically install `l10n_mx` and all its transitive dependencies as part of the installation process.

## Models Reference

No custom models are defined in this module.

## Security Groups

No custom security groups or access rules are defined in this module.

## Menus & Actions

No menus or actions are defined in this module.

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo es el punto de entrada principal de la instancia Odoo para el proyecto Promovago. Su función es actuar como módulo instalador: al instalarlo, garantiza que todos los componentes necesarios para que la instancia funcione correctamente estén presentes y configurados.

El módulo no agrega pantallas ni funcionalidad visible directamente para el usuario. En cambio, establece la base tecnológica y fiscal sobre la que opera toda la instancia, incluyendo la localización mexicana requerida para cumplir con los requisitos contables y fiscales del país.

Al ser el módulo principal de la aplicación (`"This is the app"`), su instalación desencadena la configuración completa del entorno Promovago en la instancia de Odoo.

## Objetivo de Negocio

- Proporcionar un único punto de instalación para desplegar la instancia Promovago de forma completa y reproducible.
- Garantizar que la localización mexicana (`l10n_mx`) esté siempre presente en la instancia.
- Estandarizar el entorno base de la instancia para todos los ambientes (desarrollo, staging, producción).
- Simplificar el proceso de onboarding de nuevas instancias, reduciendo el riesgo de omitir dependencias críticas.

## Flujos de Negocio Principales

### Flujo 1: Instalación inicial de la instancia Promovago

**Descripción:** Este flujo se ejecuta una única vez al momento de preparar una nueva instancia Odoo para el proyecto Promovago. Su resultado es un entorno listo para recibir los módulos de negocio específicos del cliente.

**Pasos:**
1. El administrador técnico coloca el repositorio `promovago` en el addons path de la instancia.
2. Desde **Configuración → Activar modo desarrollador → Actualizar lista de aplicaciones**, se refresca el catálogo de módulos.
3. Se busca `Instance Creator` en el listado de aplicaciones y se hace clic en **Instalar**.
4. Odoo instala automáticamente `l10n_mx` y todos sus prerrequisitos.
5. La instancia queda configurada con la localización mexicana lista para usar.

**Reglas de negocio importantes:**
- La instalación de este módulo implica la instalación obligatoria de la localización mexicana; no es posible omitirla.
- No se deben instalar instancias Promovago sin pasar por este módulo como punto de entrada.

## Guía de Configuración

1. Instalar el módulo siguiendo los pasos descritos en el flujo anterior.
2. Una vez instalado, verificar en **Configuración → Empresas** que la empresa principal tenga asignado México como país y que el plan contable mexicano (`l10n_mx`) esté activo.
3. Configurar el RFC de la empresa en **Configuración → Empresas → [Empresa] → Información fiscal**.
4. Validar que los impuestos y posiciones fiscales de la localización mexicana estén correctamente cargados desde **Contabilidad → Configuración → Impuestos**.

## Campos y Pantallas Clave

Este módulo no define campos ni pantallas propias. Toda la interfaz funcional proviene de los módulos instalados como dependencias.

## Automatizaciones y Reglas

No se detectaron automatizaciones ni acciones programadas en este módulo.

## Preguntas Frecuentes (FAQ)

**P: ¿Qué pasa si instalo este módulo en una instancia que ya tiene `l10n_mx` instalado?**
R: No hay ningún problema. Odoo detectará que `l10n_mx` ya está instalado y no lo reinstalará. El módulo `instance_creator` simplemente quedará marcado como instalado sin realizar cambios adicionales.

**P: ¿Puedo desinstalar este módulo después de que la instancia ya esté configurada?**
R: No se recomienda. Al ser el módulo principal de la aplicación Promovago, desinstalarlo podría afectar la coherencia del entorno. Si se necesita remover dependencias, se debe analizar el impacto módulo por módulo.

**P: ¿Este módulo crea datos de configuración iniciales como cuentas contables o impuestos?**
R: No directamente. Los datos contables y fiscales son creados por `l10n_mx` al instalarse. Este módulo solo declara esa dependencia.

**P: ¿Por qué existe este módulo si no tiene lógica propia?**
R: Los módulos instaladores (también llamados "glue modules" o "meta-módulos") son una práctica estándar en Odoo para definir el conjunto mínimo de dependencias de un proyecto. Facilitan el despliegue reproducible de instancias y sirven como documentación viva de qué módulos son indispensables.

**P: ¿Dónde se agregan nuevas dependencias cuando el proyecto Promovago requiere más módulos?**
R: En la lista `depends` del archivo `__manifest__.py` de este módulo. Cada nuevo módulo necesario para la instancia debe declararse ahí.

**P: ¿Este módulo es compatible con versiones anteriores de Odoo?**
R: No. Está desarrollado específicamente para Odoo 19.0 (versión `19.0.1.0.0`) y no debe instalarse en instancias con versiones anteriores.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Es el módulo instalador principal de la instancia Promovago; su instalación configura automáticamente la localización mexicana y establece la base del entorno Odoo del cliente.

**Palabras clave asociadas a este módulo:**
- Instance Creator
- Promovago
- instalador
- módulo base
- localización mexicana
- l10n_mx
- dependencias
- punto de entrada
- configuración inicial
- meta-módulo
- Jarsa
- Odoo México
- despliegue

**Casos de uso típicos:**
- "¿Cómo instalo la instancia de Promovago desde cero?"
- "¿Qué módulo debo instalar primero en una instancia nueva de Promovago?"
- "¿Por qué al instalar Instance Creator también se instala la contabilidad mexicana?"
- "¿Dónde se definen las dependencias base del proyecto Promovago?"
- "Acabo de crear una instancia de Odoo 19, ¿cuál es el primer módulo que debo instalar?"
- "¿El módulo de Promovago incluye la facturación mexicana?"

**Lo que este módulo NO hace:**
- No define modelos, campos ni vistas propias; no agrega ninguna pantalla al sistema.
- No configura automáticamente los datos fiscales de la empresa (RFC, régimen fiscal); esa configuración debe hacerse manualmente después de la instalación.
- No incluye lógica de negocio específica de Promovago; esa funcionalidad reside en módulos adicionales del proyecto.
- No es compatible con versiones de Odoo anteriores a la 19.0.
<!-- odoo-docs: last-commit=fe92b51b97f74c9922935d956089fc45b17e7a2d | updated=2026-04-06 -->
