import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';

import 'route_view.dart';

void main() => runApp(const ClearPathApp());

class ClearPathApp extends StatelessWidget {
  const ClearPathApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF39DCC0),
        brightness: Brightness.dark,
      ),
      useMaterial3: true,
    ),
    home: const MobileDemo(),
  );
}

enum DemoRole { rescue, citizen }

class MobileDemo extends StatefulWidget {
  const MobileDemo({super.key});

  @override
  State<MobileDemo> createState() => _MobileDemoState();
}

class _MobileDemoState extends State<MobileDemo> with WidgetsBindingObserver {
  static const audio = MethodChannel('clearpath/alerts');
  static const initialServer = String.fromEnvironment(
    'CLEARPATH_SERVER',
    defaultValue: 'https://clearpath-hackatonintel.onrender.com',
  );
  static const alertText = 'Emergency vehicle approaching. Yield when safe.';
  final server = TextEditingController(text: initialServer);
  final presenterCode = TextEditingController();
  DemoRole role = DemoRole.rescue;
  int vehicle = 1;
  Uri? connectedServer;
  WebSocket? socket;
  Timer? retry;
  int connection = 0;
  bool wantsConnection = false;
  bool foreground = true;
  bool changingPriority = false;
  String status = 'Disconnected';
  String? controlError;
  Map<String, dynamic>? snapshot;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    stopConnection();
    server.dispose();
    presenterCode.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      foreground = true;
      if (wantsConnection) unawaited(connect());
    } else if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.detached) {
      foreground = false;
      stopConnection();
    }
  }

  void stopConnection() {
    connection++;
    retry?.cancel();
    retry = null;
    final oldSocket = socket;
    socket = null;
    if (oldSocket != null) unawaited(oldSocket.close());
    if (snapshot?['alerted'] == true) unawaited(stopAlert());
  }

  Future<void> stopAlert() async {
    try {
      await audio.invokeMethod<void>('stop');
    } on PlatformException {
      // The visual alert is available independently of Android speech.
    } on MissingPluginException {
      // Widget tests do not register the Android speech channel.
    }
  }

  Future<void> speakAlert() async {
    try {
      await audio.invokeMethod<void>('speak', alertText);
    } on PlatformException {
      await SystemSound.play(SystemSoundType.alert);
    } on MissingPluginException {
      await SystemSound.play(SystemSoundType.alert);
    }
  }

  Uri? parseServer() {
    final uri = Uri.tryParse(server.text.trim());
    if (uri == null ||
        !uri.hasAuthority ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.hasQuery ||
        uri.hasFragment ||
        (uri.path.isNotEmpty && uri.path != '/') ||
        (uri.scheme != 'https' && !(kDebugMode && uri.scheme == 'http'))) {
      return null;
    }
    return uri;
  }

  Future<void> connect() async {
    final base = parseServer();
    if (base == null) {
      setState(() => status = 'Enter a server base URL using HTTPS.');
      return;
    }

    if (connectedServer != null && connectedServer != base) {
      presenterCode.clear();
    }
    connectedServer = base;
    stopConnection();
    final attempt = connection;
    setState(() {
      snapshot = null;
      status = 'Connecting…';
      controlError = null;
      changingPriority = false;
    });
    final uri = base.replace(
      scheme: base.scheme == 'https' ? 'wss' : 'ws',
      path: '/simulation/mobile',
      queryParameters: {
        'role': role.name,
        if (role == DemoRole.citizen) 'vehicle': '$vehicle',
      },
    );

    final http = HttpClient()..connectionTimeout = const Duration(seconds: 10);
    try {
      final feed = await WebSocket.connect(
        uri.toString(),
        customClient: http,
      ).timeout(const Duration(seconds: 15));
      if (!mounted || attempt != connection) {
        await feed.close();
        return;
      }
      socket = feed..pingInterval = const Duration(seconds: 15);
      await for (final event in feed.timeout(const Duration(seconds: 20))) {
        if (!mounted || attempt != connection) break;
        final next = jsonDecode(event as String) as Map<String, dynamic>;
        final wasAlerted = snapshot?['alerted'] == true;
        final alerted = next['alerted'] == true;
        setState(() {
          snapshot = next;
          status = 'Connected';
        });
        if (alerted && !wasAlerted) unawaited(speakAlert());
        if (!alerted && wasAlerted) unawaited(stopAlert());
      }
    } on Exception {
      // Render can take a minute to wake, and the socket can drop on Wi-Fi.
    } finally {
      http.close(force: true);
      if (mounted && attempt == connection) {
        stopConnection();
        setState(() {
          snapshot = null;
          status = wantsConnection ? 'Reconnecting…' : 'Disconnected';
        });
        if (wantsConnection && foreground) {
          retry = Timer(const Duration(seconds: 3), () => unawaited(connect()));
        }
      }
    }
  }

  Future<void> setPriority(bool enabled) async {
    final base = connectedServer;
    if (base == null) return;
    final attempt = connection;
    setState(() {
      changingPriority = true;
      controlError = null;
    });
    final http = HttpClient()..connectionTimeout = const Duration(seconds: 8);
    String? error;
    try {
      final request = await http.postUrl(base.resolve('/simulation/control'));
      request.followRedirects = false;
      request.headers.contentType = ContentType.json;
      final code = presenterCode.text.trim();
      if (code.isNotEmpty) {
        request.headers.set('X-ClearPath-Control-Token', code);
      }
      request.write(jsonEncode({'priority': enabled}));
      final result = await request.close().timeout(const Duration(seconds: 8));
      await result.drain<void>().timeout(const Duration(seconds: 8));
      if (result.statusCode == HttpStatus.forbidden) {
        error = 'Enter the presenter code for this server.';
      } else if (result.statusCode != HttpStatus.ok) {
        error = 'The simulator rejected the priority change.';
      }
    } on Exception {
      error = 'Could not send the priority change.';
    } finally {
      http.close(force: true);
      if (mounted && attempt == connection) {
        setState(() {
          changingPriority = false;
          controlError = error;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = snapshot;
    final colors = Theme.of(context).colorScheme;
    final time = (state?['time'] as num?)?.toStringAsFixed(1);
    return Scaffold(
      appBar: AppBar(title: const Text('ClearPath AI · Demo')),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 560),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
              children: [
                SegmentedButton<DemoRole>(
                  segments: const [
                    ButtonSegment(
                      value: DemoRole.rescue,
                      icon: Icon(Icons.emergency_outlined),
                      label: Text('Rescue'),
                    ),
                    ButtonSegment(
                      value: DemoRole.citizen,
                      icon: Icon(Icons.directions_car_outlined),
                      label: Text('Citizen'),
                    ),
                  ],
                  selected: {role},
                  onSelectionChanged: (selected) {
                    if (role == selected.single) return;
                    setState(() => role = selected.single);
                    if (wantsConnection) unawaited(connect());
                  },
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: server,
                  enabled: !wantsConnection,
                  decoration: const InputDecoration(
                    labelText: 'Simulator server',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.url,
                  autocorrect: false,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        time == null
                            ? status
                            : '$status · ${state!['running'] == true ? 'Running' : 'Paused'} · $time s',
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        if (wantsConnection) {
                          stopConnection();
                          setState(() {
                            wantsConnection = false;
                            snapshot = null;
                            status = 'Disconnected';
                            controlError = null;
                          });
                        } else if (parseServer() != null) {
                          setState(() => wantsConnection = true);
                          unawaited(connect());
                        } else {
                          unawaited(connect());
                        }
                      },
                      child: Text(wantsConnection ? 'Disconnect' : 'Connect'),
                    ),
                  ],
                ),
                const Divider(),
                if (role == DemoRole.rescue) ...[
                  if (state != null) RouteView(state: state),
                  const SizedBox(height: 16),
                  TextField(
                    controller: presenterCode,
                    obscureText: true,
                    autocorrect: false,
                    enableSuggestions: false,
                    decoration: const InputDecoration(
                      labelText: 'Presenter code (if required)',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Green wave and alerts'),
                    subtitle: Text(
                      '${state?['priority_signal_count'] ?? 0} signals reserved or clearing',
                    ),
                    value: state?['priority_enabled'] == true,
                    onChanged: state == null || changingPriority
                        ? null
                        : setPriority,
                  ),
                  if (controlError != null)
                    Text(controlError!, style: TextStyle(color: colors.error)),
                ] else ...[
                  DropdownButtonFormField<int>(
                    initialValue: vehicle,
                    decoration: const InputDecoration(
                      labelText: 'Simulated civilian vehicle',
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      for (var id = 1; id <= 4; id++)
                        DropdownMenuItem(value: id, child: Text('Vehicle $id')),
                    ],
                    onChanged: (id) {
                      if (id == null || id == vehicle) return;
                      setState(() => vehicle = id);
                      if (wantsConnection) unawaited(connect());
                    },
                  ),
                  const SizedBox(height: 20),
                  Semantics(
                    liveRegion: true,
                    child: Card(
                      color: state?['alerted'] == true
                          ? colors.errorContainer
                          : colors.surfaceContainerHigh,
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Text(
                          state == null
                              ? 'Connect to receive alerts.'
                              : state['alerted'] == true
                              ? alertText
                              : state['assigned'] == true
                              ? 'No active alert'
                              : 'Vehicle is outside the current scenario.',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
