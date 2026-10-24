---
title: "Authentication"
description: "Configure Portal and Admin identity providers, isolated sessions, Google callbacks, and optional Cognito invitations."
sidebar:
  order: 5
---

Portal and Admin can share identity-provider settings, but must have independent application sessions. Organization-level Entra setup is separate from their global email/password provider. Complete [preparation](../preparation/) and use the authentication stages in [installation](../installation/), or repair the Secrets independently with the commands below.

## Choose the sign-in providers

The `"Email/password setup"` prompt selects Identity Platform, Amazon Cognito, or both. When both have credentials, **one** is active through `PASSWORD_AUTH_PROVIDER` (`identity-platform` or `cognito`); configuring two does not make both serve password login concurrently. Google social OAuth is a separate option and may coexist with Cognito password login.

| Provider / setting | Keys to prepare | Notes |
| --- | --- | --- |
| Identity Platform password login | `GOOGLE_IDENTITY_API_KEY`, `GOOGLE_PROJECT_ID` | Existing Google project and enabled identity service; not the social OAuth client |
| Cognito password login | `COGNITO_REGION`, `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID`, `COGNITO_CLIENT_SECRET` | Existing pool and compatible App Client; region must match the pool ID prefix |
| Google social OAuth | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Existing OAuth client, consent configuration, authorized origins and redirect URIs |
| Active password provider | `PASSWORD_AUTH_PROVIDER` | Chooses which configured password backend is used |
| Optional reCAPTCHA Enterprise | `RECAPTCHA_API_KEY`, `RECAPTCHA_PROJECT_ID`, `RECAPTCHA_SITE_KEY` | Separate registration protection, not an identity provider or replacement for MFA |
| Email auto-verification | `AUTO_VERIFY_EMAIL_ON_SIGNUP` | Starts `false`; enabling skips proof of email ownership and needs explicit risk approval |

AWS discovery can list pools/clients and retrieve the client secret only when an already authenticated operator identity is authorized. Manual entry remains possible. Discovery does not provision a pool, App Client, project, Google OAuth client, or Entra application. Do not confuse successful discovery with permission for a running Pod to call invitation APIs.

## Keep sessions isolated

| Setting | Portal | Admin |
| --- | --- | --- |
| Namespace / Secret | `moonin/moonin-front-secret` | `moonin/moonin-admin-ui-secret` |
| `NEXTAUTH_URL` | `https://portal.example.com` | `https://admin.example.com` |
| `NEXTAUTH_SECRET` | Independent generated/approved secret | Different independent generated/approved secret |
| `NEXTAUTH_COOKIE_PREFIX` | `moonin-portal` | Explicitly choose `moonin-admin` |

URLs are placeholders: replace them with your approved HTTPS hosts, without an application path. The installer can generate missing session secrets and proposes keeping existing values. Rotating one invalidates sessions for that application; it does not sign users into the other application automatically.

**New Admin cookie warning:** Admin calls the same cookie-prefix chooser as Portal. If no prefix exists, the displayed default can be `moonin-portal`. Enter `moonin-admin` explicitly. Accepting the shared provider settings is not permission to share cookie names, URLs, or session encryption/signing secrets. Cookie prefixes accept letters, numbers, hyphens, and underscores.

Portal's chart reference is `moonin-portal-ui.portalSecret.existingSecret`; align custom Secret names and namespaces with the actual chart. Admin uses its separate Secret. A missing Admin `NEXTAUTH_SECRET` breaks sessions even when all provider credentials exist.

## Portal configuration and defaults

```bash
moonin-installer portal configure
```

The independent Portal wizard asks for `"Portal namespace"` (default `moonin`) and `"Portal Secret name"` (default `moonin-front-secret`). Keep these defaults unless you have coordinated matching chart changes. It reads existing values and offers to preserve them.

| English prompt / decision | Action |
| --- | --- |
| `"Generate a secure NEXTAUTH session secret"` | When missing, generation defaults to **Yes**; do not reuse the Admin secret |
| `"Keep existing Portal public URL"` | Defaults to **Yes** when present; otherwise enter the approved Portal URL |
| `"Cookie prefix"` | Set `moonin-portal`; keeping an existing prefix defaults to **Yes** |
| Google OAuth | New setup starts disabled; `Keep current` preserves existing credentials |
| `"Email/password setup"` | Select the backend(s), supply provider-issued credentials, and review the active backend |
| `"Configure reCAPTCHA Enterprise for registration protection"` | Initially disabled if no existing complete setup; supply all three keys only if your registration uses it |
| Apply reviewed authentication Secret | Review the target and non-secret status before accepting |

For Identity Platform, `AUTO_VERIFY_EMAIL_ON_SIGNUP` initially remains `false`; an existing `true` can be retained by its flow. Cognito sets it to `false`. Prefer actual verification rather than auto-verifying Enterprise accounts.

## Admin reuse and independent repair

```bash
moonin-installer platform auth admin configure
```

If Portal's Secret exists, `"Reuse shared sign-in provider settings from Moonin Portal"` defaults to **Yes**. This copies the active password-provider choice, Identity Platform/Cognito credentials, Google OAuth credentials, reCAPTCHA keys, and email auto-verification setting. Shared keys absent from Portal are **removed from Admin** during synchronization; review this when intentionally keeping different provider configurations.

Admin then keeps or generates its own `NEXTAUTH_SECRET`, asks for its public URL and cookie prefix, and, for active Cognito, detects/requests an invitation role. `"Apply the Admin UI authentication Secret"` defaults to **Yes**. Decline provider reuse if Admin must have independently managed providers.

Changing Portal does not synchronize Admin in the background. Run the Admin command again and explicitly accept reuse when you intend to sync. These commands update Secrets, **not Helm releases or running processes**. Arrange a controlled rollout/redeploy of every consuming workload and verify readiness before testing. Environment variables sourced through `envFrom` do not refresh in existing Pods just because a Secret changed.

## Google domains and callbacks

Prepare authorized domains in your Google identity/project settings, browser origins, and the exact OAuth redirect URIs. For Google social OAuth, the standard NextAuth callback paths for the example hosts are:

```text
Authorized origins:
https://portal.example.com
https://admin.example.com

Authorized redirect URIs:
https://portal.example.com/api/auth/callback/google
https://admin.example.com/api/auth/callback/google
```

Use the actual external scheme/host and the callback path supported by your deployed application's configuration. Do not register a guessed wildcard callback or leave suggested hosted-service domains. If using separate Google clients, register each application's callback with its own client and configure Admin independently instead of blindly reusing credentials. Identity Platform authorized domains are a separate setting from social OAuth redirect URIs.

Match DNS, load-balancer routing, ingress TLS, `NEXTAUTH_URL`, OAuth configuration, and any organization-level Entra redirect settings. The installer saves application configuration; it does not provision provider accounts or prove domain ownership. Test sign-in and logout from the real browser-facing URLs.

## Optional Cognito: TOTP and invitations

Cognito is an **optional provider**, not a mandatory dependency for every Enterprise deployment. If selected, configure the pool for software-token TOTP and the flows expected by the deployed applications. A pool with MFA set to `OPTIONAL` can support per-user TOTP enrollment; that does **not** mean production non-demo users may skip the application's server-side MFA checks. Current non-demo password flows enforce MFA enrollment/challenges. Test temporary-password changes, enrollment, six-digit authenticator challenges, recovery, and clock accuracy before rollout.

Demo identities have special behavior and can bypass normal checks. Do not enable or publish a demo account in an Enterprise installation to work around enrollment, email verification, or MFA failures. A private test account should exercise the same security policy as real users. Coordinate MFA recovery with your identity administrator rather than weakening the provider or changing stored user data manually.

For Admin invitations on EKS, prepare a workload IAM role using **IRSA**, independently from the operator's AWS CLI login. Its web-identity trust must reference your cluster's OIDC provider, audience `sts.amazonaws.com`, and the exact subject:

```text
system:serviceaccount:moonin:moonin-admin-ui
```

Grant only the needed actions `cognito-idp:AdminCreateUser` and `cognito-idp:AdminGetUser`, scoped to the intended user-pool resource. Annotate the actual Admin ServiceAccount with the approved role using your infrastructure process; the installer can detect or request the role ARN, not create Pod credentials by copying workstation credentials. Do not inject static AWS access keys into application Secrets. EBS CSI's Pod Identity setup is a separate storage concern, not this invitation role's trust model.

The Cognito invitation template must include `{username}` and `{####}`. Prepare sender identity, SES configuration when applicable, sandbox restrictions, recipient authorization, quotas, and deliverability. An existing role/pool is not proof of successful email delivery. Validate an invitation to an approved non-demo test user and the first-login/password/MFA sequence.

## Authentication acceptance

1. Verify trusted HTTPS for both real hosts and no redirect to an unintended domain.
2. Sign in independently to Portal and Admin; test logout and cookie/session isolation.
3. Confirm initial owner access and organization boundaries, not merely successful identity-provider authentication.
4. Test the active password provider, email verification, MFA when applicable, and optional Google login.
5. Test invitation authorization and actual email receipt; confirm unauthorized users cannot gain access.
6. After any Secret change, confirm consuming Pods were redeployed and are healthy. Redact all credentials from diagnostic evidence.

See [operations](../operations/) for repair, restart planning, and diagnosis without printing Secret values.