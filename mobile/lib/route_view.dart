import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:material_ui/material_ui.dart';

class RouteView extends StatelessWidget {
  const RouteView({required this.state, super.key});

  final Map<String, dynamic> state;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final route = (state['route'] as List).map(readPoint).toList();
    final location = state['position'];
    final kilometers = (state['route_meters'] as num) / 1000;
    final minutes = (state['route_seconds'] as num) / 60;
    final routeStatus = switch (state['route_status']) {
      'en_route' => 'En route',
      'arrived' => 'Arrived',
      'awaiting_dispatch' => 'Waiting for dispatch',
      _ => 'Route blocked',
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(routeStatus, style: Theme.of(context).textTheme.headlineSmall),
        if (state['dispatch_destination'] case final String destination)
          Text(destination),
        if (state['route_status'] != 'awaiting_dispatch')
          Text(
            '${kilometers.toStringAsFixed(2)} km · ${minutes.toStringAsFixed(1)} modeled min',
          ),
        if (route.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Semantics(
              label: 'Rescue route preview',
              child: SizedBox(
                width: double.infinity,
                height: 190,
                child: CustomPaint(
                  painter: RoutePainter(
                    route: route,
                    position: location == null ? null : readPoint(location),
                    lineColor: colors.primary,
                    markerColor: colors.tertiary,
                    backgroundColor: colors.surfaceContainerHigh,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Offset readPoint(dynamic value) {
    final coordinates = value as List;
    return Offset(
      (coordinates[0] as num).toDouble() * .76,
      -(coordinates[1] as num).toDouble(),
    );
  }
}

class RoutePainter extends CustomPainter {
  const RoutePainter({
    required this.route,
    required this.position,
    required this.lineColor,
    required this.markerColor,
    required this.backgroundColor,
  });

  final List<Offset> route;
  final Offset? position;
  final Color lineColor;
  final Color markerColor;
  final Color backgroundColor;

  @override
  void paint(Canvas canvas, Size size) {
    const padding = 18.0;
    final background = RRect.fromRectAndRadius(
      Offset.zero & size,
      const Radius.circular(16),
    );
    canvas.drawRRect(background, Paint()..color = backgroundColor);

    final points = [...route, ?position];
    final xs = points.map((point) => point.dx);
    final ys = points.map((point) => point.dy);
    final left = xs.reduce(math.min);
    final top = ys.reduce(math.min);
    final width = math.max(xs.reduce(math.max) - left, .0001);
    final height = math.max(ys.reduce(math.max) - top, .0001);
    final scale = math.min(
      (size.width - 2 * padding) / width,
      (size.height - 2 * padding) / height,
    );
    final inset = Offset(
      (size.width - width * scale) / 2,
      (size.height - height * scale) / 2,
    );
    Offset project(Offset point) => inset + (point - Offset(left, top)) * scale;

    final path = Path()..addPolygon(route.map(project).toList(), false);
    canvas.drawPath(
      path,
      Paint()
        ..color = lineColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
    canvas.drawCircle(project(route.last), 5, Paint()..color = lineColor);
    if (position case final rescue?) {
      canvas.drawCircle(project(rescue), 7, Paint()..color = markerColor);
    }
  }

  @override
  bool shouldRepaint(covariant RoutePainter oldDelegate) =>
      position != oldDelegate.position ||
      !listEquals(route, oldDelegate.route) ||
      lineColor != oldDelegate.lineColor ||
      markerColor != oldDelegate.markerColor ||
      backgroundColor != oldDelegate.backgroundColor;
}
