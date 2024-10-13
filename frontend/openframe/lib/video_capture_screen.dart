import 'dart:async';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

class VideoCaptureScreen extends StatefulWidget {
  const VideoCaptureScreen({super.key});

  @override
  State<VideoCaptureScreen> createState() => _VideoCaptureScreenState();
}

class _VideoCaptureScreenState extends State<VideoCaptureScreen> {
  CameraController? _controller;
  List<CameraDescription>? cameras;
  bool isRecording = false;
  late String videoPath;
  Timer? frameTimer;
  int count = 15;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    cameras = await availableCameras();
    _controller = CameraController(cameras![0], ResolutionPreset.high);
    await _controller?.initialize();
    setState(() {});
  }

  Future<void> _startVideoRecording() async {
    // await _controller?.startImageStream();
    _initializeCamera();
    await _controller?.startVideoRecording();
    setState(() {
      isRecording = true;
      count = 15;
    });

    // Capture frames every second
    frameTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      count--;
      if (count <= 0) {
        _stopVideoRecording();
      }
      setState(() {});
      await _captureFrame();
    });
  }

  Future<void> _stopVideoRecording() async {
    frameTimer?.cancel();
    // await _controller?.stopImageStream();
    await _controller?.stopVideoRecording();
    setState(() {
      isRecording = false;
    });
  }

  Future<void> _captureFrame() async {
    if (_controller?.value.isTakingPicture == true) {
      return;
    }

    final image = await _controller?.takePicture();
    if (image != null) {
      final savedImage = File(image.path);
      // You can process or save the image frame as needed
      final bytes = await savedImage.readAsBytes();

      // Now you can use the bytes as needed
      // ignore: avoid_print
      print('Frame captured with ${bytes.length} bytes');
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    frameTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Video Capture')),
      body: Column(
        children: [
          if (_controller != null && _controller!.value.isInitialized)
            AspectRatio(
              aspectRatio: 0.7,
              child: CameraPreview(_controller!),
            ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: isRecording ? _stopVideoRecording : _startVideoRecording,
            child: Text(isRecording ? 'Stop Recording' : 'Start Recording'),
          ),
          Text("${count}s"),
        ],
      ),
    );
  }
}
