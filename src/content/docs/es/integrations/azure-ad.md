---
title: "Azure AD"
---

Moonin soporta Microsoft Entra ID a nivel de organización. La integración se configura en la Consola Admin y luego es usada tanto por la app principal como por la app administrativa.

## Para qué sirve esta integración

Usa Azure AD cuando necesitas:

- inicio de sesión Microsoft específico por organización
- acceso corporativo guiado por dominio
- un punto de entrada SSO compartible basado en slug
- membresia base automática para usuarios que ingresan por la organización configurada

## Donde se configura

Azure AD se configura dentro del registro de la organización en la Consola Admin.

Campos requeridos:

- slug de la organización
- Azure AD habilitado
- tenant ID
- client ID
- client secret

Campos opcionales pero importantes:

- primary domain
- domains adicionales
- authority host

## Modelo de resolución para el inicio de sesión

Moonin primero necesita determinar a qué organización quiere entrar el usuario.

Puede resolverlo desde:

- el slug de la organización
- el primary domain
- cualquiera de los domains adicionales configurados
- el dominio del email usado como hint durante el login

## Flujo de login con Azure AD

```mermaid
flowchart LR
    A[Usuario abre login de Moonin]
    B[Moonin resuelve la organización por slug o dominio]
    C[Se carga el provider Azure AD de esa organización]
    D[El usuario inicia sesión con Microsoft]
    E[Moonin asegura que exista el usuario backend]
    F[Se define la organización por defecto]
    G[Se asegura membership viewer]

    A --> B --> C --> D --> E --> F --> G
```

## Qué ocurre después de un login Microsoft exitoso

Cuando el login pertenece a una organización valida con Azure habilitado, Moonin:

- crea o reutiliza el usuario backend
- ajusta la organización por defecto de ese usuario si hace falta
- asegura al menos una membership `viewer` dentro de la organización

Esta es una regla operativa importante:

- el login Azure AD entrega membresia base en la organización
- esa membresia base es `viewer` y sigue mínimo privilegio por defecto
- por defecto eso significa que el usuario puede listar organizaciones y solo expande acceso con permisos asignados por un admin
- no convierte automáticamente al usuario en admin, editor u owner
- los privilegios superiores siguen otorgandose por cambios de membership, roles directos o grupos

## Link de acceso basado en slug

Moonin puede generar un link compartible de ingreso específico por organización usando el slug. Este es el punto de entrada recomendado para usuarios finales porque elimina ambiguedad sobre que configuración debe usarse.

Usa el link con slug cuando:

- la misma empresa opera más de una organización en Moonin
- quieres que el usuario aterrice directo en el tenant correcto
- no quieres depender solo de descubrimiento por dominio del email

## Campos de dominio y por que importan

- `primary_domain` identifica el dominio principal del negocio
- `domains` permite agregar dominios alternativos
- esos valores ayudan a Moonin a resolver la organización desde hints de login

Esto es especialmente útil cuando los usuarios no comienzan desde el link con slug.

## Guia operativa

1. Define primero el slug de la organización.
2. Agrega el primary domain y cualquier dominio secundario.
3. Habilita Azure AD y completa tenant, client y secret.
4. Prueba la URL de login con slug.
5. Comparte esa URL con los usuarios finales.
6. Después del primer ingreso, revisa si el usuario necesita solo `viewer` o permisos adicionales.

## Expectativas comunes

- una sola organización con Azure habilitado basta para activar ese flujo de ingreso
- la configuración por organización es la que determina qué provider Azure se usa al hacer login
- una cosa es que el login sea exitoso y otra el nivel de autorización dentro de Moonin

Si el login Microsoft funciona pero el usuario no puede gestionar recursos, normalmente el problema son permisos Moonin faltantes y no Azure AD.
