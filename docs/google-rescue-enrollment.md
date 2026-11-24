# Google sign-in and Rescue enrollment

Google sign-in for **Hackathon-supa** was disabled when checked on 24 November 2026. The existing authenticated rehearsal uses the three Supabase email/password demo accounts. The Android simulator app currently joins the synthetic feed and uses a separate presenter code for write controls.

## Configure Google sign-in

The project owner uses a Google Cloud **Web application** OAuth client for ClearPath. Set this exact authorized redirect URI on the Google client:

```text
https://uodbkiyevjwgmjnofcpj.supabase.co/auth/v1/callback
```

Enable Google in **Supabase → Authentication → Sign In / Providers** and enter the client credentials there. Register the selected application's callback separately in Supabase's redirect allowlist. For a Google consent screen in testing mode, add the intended users as test users. Keep the Google client secret in the provider settings. [Supabase Google OAuth guide](https://supabase.com/docs/guides/auth/social-sign-in/auth-google)

## Enroll the selected Rescue users

Once Google sign-in works, each selected user signs in with their intended Google account. An administrator matches the verified Google identity in **Supabase → Authentication → Users** and grants that Auth user UUID the `rescue` role in `clearpath.users`. Add a corresponding row in `clearpath.units` using the vehicle type that person will operate. Existing roles should be reviewed before changing them.

The user's Google identity establishes who signed in. The ClearPath database role establishes what they can do. An administrator grants each Rescue role, and a dispatcher creates each assignment. A Rescue role allows priority requests only while the user's unit has an active assignment on an open incident. [Dispatch schema and rehearsal](dispatch.md)
