# ClearPath Android demo

Open the rescue and citizen screens on an Android phone, or use two phones for a synchronized rehearsal. Both roles use the same FastAPI instance as the desktop simulator.

## Run on Android

Install Flutter 3.50 with the Android SDK and enable USB debugging on the phone. From the mobile directory, run:

```powershell
flutter pub get
flutter run
```

The default server is the public Render service. Tap **Connect** and open the [desktop simulator](https://clearpath-hackatonintel.onrender.com/simulator) on the demo laptop. Give Render time to wake up if it has been idle. For a local rehearsal, start FastAPI using the [partner guide](../user.md), then run the following commands from the mobile directory with the phone connected by USB:

```powershell
adb reverse tcp:8000 tcp:8000
flutter run --dart-define=CLEARPATH_SERVER=http://127.0.0.1:8000
```

The local HTTP and WebSocket connection is available in debug builds. Use an HTTPS base URL for a release build. For a private Wi-Fi rehearsal, point the phone and browser at the same reachable HTTPS endpoint.

## Rehearse the demo

1. In the desktop simulator, reset to Bellevue Hospital → Times Square and leave playback paused. In the app, select **Rescue** and connect. Check that the route preview and clock match the desktop.
2. On the second phone select **Citizen**, keep **Vehicle 1**, and connect to the same server. In the initial scenario, Vehicle 1 starts in range. Leave the app visible and turn up media volume for the spoken alert.
3. For the shared public demo, unlock **Presenter access** in the desktop browser and toggle **Green wave and alerts** off and on there. Neither Android viewer needs the code to follow the scenario. The citizen alert clears and returns. If the demo specifically shows Android changing priority, enter the Render presenter code in Rescue and use its switch. The standard local setup has open presenter controls.
4. Close a road on the desktop route and verify that the phone shows the updated route. Reopen the road. Start and pause playback and verify the same simulation clock on both phones.

FastAPI streams position and route updates to Rescue and alert state to Citizen. The Android app speaks new alerts while in the foreground. Android location permissions and background push are outside this rehearsal.

The existing GitHub container check exercises both streams and presenter authorization. Run `flutter analyze` and `flutter test` from the mobile directory after editing the app.
