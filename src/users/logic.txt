# LogIt: Users Module Plan

Planning notes for src/users/.


## File Breakdown (src/users/)

- model         User table definition
- routes        API endpoints: sign up, log in, log out, get/update profile
- service       Logic behind the routes (create user, check password).
                Keeps routes thin and makes logic easy to test and reuse.
- validation    Input rules: email format, username rules, password length
- auth middleware
                Checks who is logged in on each request. Used by every other
                feature, so it can also live in src/shared/.
- tests


## User Fields (Start)

- id              UUID (sequential ids in URLs reveal how many users exist)
- email           Unique, stored lowercase
- username        Unique, case-insensitive, used in public profile URLs.
                  Reserve names like "admin", "settings", "login".
- password_hash   Never store the plain password
- display_name
- created_at
- updated_at

Add bio, avatar, and settings later. Keep the User table slim.


## Features

### Phase 1
- [ ] Sign up
- [ ] Log in / log out
- [ ] Sessions (cookie-based sessions are simplest for a web app)
- [ ] "Current user" endpoint so the frontend knows who is logged in
- [ ] Edit basic profile info

### Later
- [ ] Password reset and email verification (needs an email service)
- [ ] Sign in with Google
- [ ] Public profile pages (Phase 3)
- [ ] Follow other users (Phase 3, likely its own src/social/ folder)
- [ ] Account deletion


## Things to Get Right Early

1. Don't build auth from scratch (unless learning it is the goal).
   Use your framework's built-in auth or a library/service
   (e.g., Django auth, Auth.js, Supabase Auth, Clerk).
   If writing it yourself:
   - Hash passwords with bcrypt or argon2
   - Rate-limit login attempts
   - Use a generic error ("invalid email or password") so attackers
     can't learn which emails have accounts

2. Separate public and private fields.
   When returning another user's data, send only public fields
   (username, display name), never email or password hash.
   Write one "public user" formatting function and use it everywhere.

3. Authorization, not just authentication.
   Logging in proves who someone is; you also need to check what they can do.
   Every endpoint touching a list or entry must check that the requester
   owns it or that it is public. Put this check in one place.

4. Reference users by id internally.
   Treat username as a display label. If lists point to usernames,
   a username change breaks them.

5. Decide what account deletion does.
   Topics a user created that others use should survive deletion:
   keep the topic and clear its creator field.


## Build Order

1. User model
2. Sign up
3. Log in / sessions
4. "Current user" endpoint
5. Auth middleware
6. Then move on to lists


## Edge Cases to Test Before Moving On

- [ ] Sign up with an email that already exists
- [ ] Sign up with a reserved or duplicate username (different capitalization)
- [ ] Log in with a wrong password
- [ ] Access a protected endpoint while logged out
- [ ] Try to view or edit another user's private list
