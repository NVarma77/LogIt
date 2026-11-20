# 002: Custom User model from the first migration

Status: Accepted (2026-11-19)

## Context
Django lets you replace the built-in `auth.User`, but only cheaply before the first migration;
changing `AUTH_USER_MODEL` later means hand-rewriting migrations and foreign keys. The users
plan (`docs/notes/users.md`) needs UUID ids, a unique lowercase email, and usernames that are unique
ignoring case and safe to use in profile URLs.

## Options
1. Use the built-in `auth.User` and add a `Profile` one-to-one table.
2. `User(AbstractUser)`: keep Django's fields and auth machinery, override what we need.
3. `User(AbstractBaseUser)`: define every field from scratch.

## Choice
Option 2, in `apps/accounts/models.py`:
- `id`: UUID4 primary key.
- `username`: stored as typed, max 30, `^[A-Za-z0-9_]{3,30}$`, not on a reserved-names list.
  Unique ignoring case via a functional unique index on `Lower(username)`.
- `email`: unique, always lowercase. `UserManager.normalize_email` is overridden to lowercase
  the whole address (Django only lowercases the domain). `create_user`, `create_superuser`, and
  `Model.clean()` all call it, so every path is covered. A `CHECK (email = lower(email))`
  constraint guarantees it.
- `display_name`, `updated_at`; `date_joined` serves as created_at.
- Sign-up goes through `accounts.services.register_user`, which runs `full_clean()` and the
  password validators.

## Why
- **AbstractUser over AbstractBaseUser:** admin, permissions, and auth forms keep working with
  almost no code. Tradeoff: we inherit fields we may not use (first_name, last_name).
- **UUID primary key:** sequential ids in URLs reveal how many users exist and let anyone enumerate
  accounts. Tradeoff: 16-byte keys and random insert order make indexes a bit larger and less
  cache-friendly than bigint; irrelevant at this scale.
- **Case rules in the database, not only in Python:** `full_clean()` gives friendly form errors,
  but `.update()`, bulk writes, or two concurrent sign-ups skip it. The functional unique index and
  check constraint make the invariants hold no matter which code path writes. Tests cover both
  layers.
- **Reserved names in code, not a DB constraint:** the list is policy that will grow. A
  constraint would need a migration per change and would fail for any existing user who already
  has a newly reserved name.
- **ASCII-only usernames:** blocks look-alike impersonation ("аdmin" with a Cyrillic "а") and keeps
  URLs clean. Tradeoff: users with non-Latin names can't use their own script in their username,
  but their `display_name` can be anything.
- **Lowercasing the whole email:** the RFC lets the local part be case-sensitive, but in practice
  providers ignore case, and treating `Neel@x.com` and `neel@x.com` as two accounts causes more harm.

## Rejected
- **Built-in User + Profile:** keeps a case-sensitive username and integer ids, and every
  profile read needs a join.
- **Lowercasing usernames on save:** simpler uniqueness, but it throws away the capitalization
  the user chose ("NeelV").
- **`citext` columns:** another extension, and Django's `CICharField` is deprecated in favor of
  functional indexes or collations.

## At 100x scale
The User table stays small and hot; the questions are about auth traffic. Sessions would move from
the database to Redis, login gets rate limiting (planned), and email verification plus OAuth are
needed before any public launch. Nothing in this schema needs to change.

## Deferred
- Case-insensitive login ("neelv" logs into "NeelV"): decide in Slice 1 when login exists.
