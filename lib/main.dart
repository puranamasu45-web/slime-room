import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const SlimeRoomApp());
}

class SlimeRoomApp extends StatelessWidget {
  const SlimeRoomApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'slime_room',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF42C7F5)),
        useMaterial3: true,
      ),
      home: const SlimeTapPage(),
    );
  }
}

class SlimeTapPage extends StatefulWidget {
  const SlimeTapPage({super.key});

  @override
  State<SlimeTapPage> createState() => _SlimeTapPageState();
}

class _SlimeTapPageState extends State<SlimeTapPage>
    with SingleTickerProviderStateMixin {
  static const int goalTaps = 10000;
  static const String _saveKey = 'slime_tap_count';

  late final AnimationController _jumpController;
  int _tapCount = 0;
  bool _loaded = false;

  double get _progress => (_tapCount / goalTaps).clamp(0.0, 1.0);
  bool get _cleared => _tapCount >= goalTaps;

  @override
  void initState() {
    super.initState();
    _jumpController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 280),
    );
    _loadTapCount();
  }

  @override
  void dispose() {
    _jumpController.dispose();
    super.dispose();
  }

  Future<void> _loadTapCount() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) {
      return;
    }
    setState(() {
      _tapCount = prefs.getInt(_saveKey) ?? 0;
      _loaded = true;
    });
  }

  Future<void> _saveTapCount() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_saveKey, _tapCount);
  }

  Future<void> _tapSlime() async {
    if (!_loaded || _cleared) {
      _jumpController.forward(from: 0);
      return;
    }

    setState(() {
      _tapCount += 1;
    });
    _jumpController.forward(from: 0);
    await _saveTapCount();

    if (!mounted) {
      return;
    }

    if (_tapCount == goalTaps) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ゴール！スライムは10000回跳ねきった！')),
      );
    }
  }

  Future<void> _resetTapCount() async {
    final reset = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('リセットする？'),
          content: const Text('タップ数を0に戻します。'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('やめる'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('リセット'),
            ),
          ],
        );
      },
    );

    if (reset != true) {
      return;
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_saveKey, 0);
    if (!mounted) {
      return;
    }
    setState(() {
      _tapCount = 0;
    });
    _jumpController.forward(from: 0);
  }

  String _slimeLine() {
    if (_cleared) {
      return 'ゴール！もちもち完全勝利！';
    }
    if (_tapCount >= 9000) {
      return 'あと少し。ゴールが見える！';
    }
    if (_tapCount >= 7000) {
      return 'もちもち全開で跳ねてる！';
    }
    if (_tapCount >= 5000) {
      return '半分きた！湯気も元気！';
    }
    if (_tapCount >= 3000) {
      return 'ちょっと楽しくなってきた。';
    }
    if (_tapCount >= 1000) {
      return 'まだまだ跳ねるよ。';
    }
    if (_tapCount > 0) {
      return 'ぷるん。';
    }
    return 'スライムをタップして10000回跳ねよう。';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFEAF9FF), Color(0xFFFFF6E5)],
          ),
        ),
        child: SafeArea(
          child: _loaded
              ? Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'slime_room',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.5,
                            ),
                          ),
                          TextButton.icon(
                            onPressed: _resetTapCount,
                            icon: const Icon(Icons.refresh),
                            label: const Text('Reset'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '$_tapCount / $goalTaps',
                        style: const TextStyle(
                          fontSize: 34,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(999),
                        child: LinearProgressIndicator(
                          minHeight: 16,
                          value: _progress,
                          backgroundColor: Colors.white.withValues(alpha: 0.75),
                        ),
                      ),
                      const SizedBox(height: 28),
                      Expanded(
                        child: Center(
                          child: GestureDetector(
                            behavior: HitTestBehavior.opaque,
                            onTap: _tapSlime,
                            child: AnimatedBuilder(
                              animation: _jumpController,
                              builder: (context, child) {
                                final wave = math.sin(_jumpController.value * math.pi);
                                final squash = math.sin(_jumpController.value * math.pi * 2);
                                return Transform.translate(
                                  offset: Offset(0, -34 * wave),
                                  child: Transform.scale(
                                    scaleX: 1 + (0.08 * squash.abs()),
                                    scaleY: 1 - (0.05 * squash.abs()),
                                    child: child,
                                  ),
                                );
                              },
                              child: CustomPaint(
                                size: const Size(240, 220),
                                painter: SlimePainter(
                                  progress: _progress,
                                  cleared: _cleared,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      AnimatedSwitcher(
                        duration: const Duration(milliseconds: 220),
                        child: Text(
                          _slimeLine(),
                          key: ValueKey<String>(_slimeLine()),
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      FilledButton.tonalIcon(
                        onPressed: _tapSlime,
                        icon: const Icon(Icons.touch_app),
                        label: const Text('スライムをタップ'),
                      ),
                    ],
                  ),
                )
              : const Center(child: CircularProgressIndicator()),
        ),
      ),
    );
  }
}

class SlimePainter extends CustomPainter {
  const SlimePainter({
    required this.progress,
    required this.cleared,
  });

  final double progress;
  final bool cleared;

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final bodyRect = Rect.fromLTWH(w * 0.09, h * 0.18, w * 0.82, h * 0.66);

    final shadowPaint = Paint()
      ..color = Colors.black.withValues(alpha: 0.13)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 14);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w / 2, h * 0.87),
        width: w * 0.62,
        height: h * 0.11,
      ),
      shadowPaint,
    );

    final bodyPath = Path()
      ..moveTo(w * 0.50, h * 0.12)
      ..cubicTo(w * 0.20, h * 0.16, w * 0.07, h * 0.48, w * 0.15, h * 0.68)
      ..cubicTo(w * 0.21, h * 0.86, w * 0.37, h * 0.88, w * 0.50, h * 0.84)
      ..cubicTo(w * 0.63, h * 0.88, w * 0.79, h * 0.86, w * 0.85, h * 0.68)
      ..cubicTo(w * 0.93, h * 0.48, w * 0.80, h * 0.16, w * 0.50, h * 0.12)
      ..close();

    final bodyPaint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Color(0xFF7BE9FF), Color(0xFF25AEEA)],
      ).createShader(bodyRect);
    canvas.drawPath(bodyPath, bodyPaint);

    final rimPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 5
      ..color = Colors.white.withValues(alpha: 0.55);
    canvas.drawPath(bodyPath, rimPaint);

    final highlightPaint = Paint()..color = Colors.white.withValues(alpha: 0.48);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.36, h * 0.34),
        width: w * 0.20,
        height: h * 0.10,
      ),
      highlightPaint,
    );

    final eyePaint = Paint()..color = const Color(0xFF17506C);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.39, h * 0.51),
        width: w * 0.075,
        height: h * 0.11,
      ),
      eyePaint,
    );
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.61, h * 0.51),
        width: w * 0.075,
        height: h * 0.11,
      ),
      eyePaint,
    );

    final eyeLightPaint = Paint()..color = Colors.white.withValues(alpha: 0.85);
    canvas.drawCircle(Offset(w * 0.375, h * 0.48), w * 0.012, eyeLightPaint);
    canvas.drawCircle(Offset(w * 0.585, h * 0.48), w * 0.012, eyeLightPaint);

    final cheekPaint = Paint()..color = const Color(0xFFFF87A6).withValues(alpha: 0.50);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.28, h * 0.60),
        width: w * 0.12,
        height: h * 0.05,
      ),
      cheekPaint,
    );
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.72, h * 0.60),
        width: w * 0.12,
        height: h * 0.05,
      ),
      cheekPaint,
    );

    final mouthPaint = Paint()
      ..color = const Color(0xFF17506C)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    final mouthPath = Path();
    if (cleared) {
      mouthPath.moveTo(w * 0.43, h * 0.63);
      mouthPath.cubicTo(w * 0.48, h * 0.70, w * 0.52, h * 0.70, w * 0.57, h * 0.63);
    } else {
      mouthPath.moveTo(w * 0.45, h * 0.63);
      mouthPath.quadraticBezierTo(w * 0.50, h * 0.67, w * 0.55, h * 0.63);
    }
    canvas.drawPath(mouthPath, mouthPaint);

    final steamPaint = Paint()
      ..color = const Color(0xFF9FE8FF).withValues(alpha: 0.22)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 5
      ..strokeCap = StrokeCap.round;

    for (var i = 0; i < 3; i++) {
      final x = w * (0.34 + i * 0.16);
      final yOffset = math.sin((progress * 10) + i) * 4;
      final steam = Path()
        ..moveTo(x, h * 0.12 + yOffset)
        ..cubicTo(x - 10, h * 0.02 + yOffset, x + 10, h * -0.02 + yOffset, x, h * -0.10 + yOffset);
      canvas.drawPath(steam, steamPaint);
    }
  }

  @override
  bool shouldRepaint(covariant SlimePainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.cleared != cleared;
  }
}
