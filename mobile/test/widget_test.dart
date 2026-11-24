import 'package:clearpath_mobile/main.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Citizen does not see rescue priority controls', (tester) async {
    await tester.pumpWidget(const ClearPathApp());
    expect(find.byType(SwitchListTile), findsOneWidget);

    await tester.tap(find.text('Citizen'));
    await tester.pumpAndSettle();

    expect(find.byType(SwitchListTile), findsNothing);
    expect(find.text('Connect to receive alerts.'), findsOneWidget);
  });
}
