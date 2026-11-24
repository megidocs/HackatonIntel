# Rescue sign-in for the hackathon

## Amit’s demo on Lenovo

1. Start the [local dispatch service](dispatch.md#start-with-the-private-local-file) and open [ClearPath sign-in](http://127.0.0.1:8003/dispatch/reports).
2. In Lenovo’s Git-ignored `.env.dispatch.local`, find `CLEARPATH_DEMO_RESCUE_EMAIL` and `CLEARPATH_DEMO_RESCUE_PASSWORD`. Enter those values privately and select **Sign in**. The page shows **Signed in as rescue** and the vehicle’s current assignment.
3. Have a dispatcher sign in separately and approve a demo assignment. Amit can click **Refresh assignment** to load the change.
4. For the public Android simulator, open ClearPath, select **Rescue**, and tap **Connect**. The desktop presenter controls the shared scenario. To show the phone changing signal priority, use the separate presenter code in the app.

The private file location is in [user.md](../user.md). The demo Rescue login works on the laptop’s signed-in dispatch site. The [public simulator](https://clearpath-hackatonintel.onrender.com/simulator) offers the synthetic browser and phone feeds.

## Named accounts after the demo

Hackathon-supa has Supabase email/password sign-in available. An administrator can enroll a person once their email address is verified in Supabase Auth. The existing database role check then controls their assignment visibility and priority requests.

From the repository root on the owner’s signed-in CLI, preview an exact account address first, then perform the enrollment:

```powershell
.\.venv\Scripts\python.exe -m backend.enroll_rescue verified-user@example.com
.\.venv\Scripts\python.exe -m backend.enroll_rescue verified-user@example.com --vehicle medical --apply
```

Existing dispatchers retain that role. Existing Rescue unit types are retained. The administrator chooses a type when creating a new unit. The project’s default email service limits confirmation and magic-link deliveries to project team addresses, so use the pre-enrolled password account for the rehearsal. [Supabase email delivery limits](https://supabase.com/docs/guides/auth/auth-smtp)
