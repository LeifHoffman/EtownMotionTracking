<?php
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo 'Method Not Allowed';
    exit;
}

$athleteName = trim($_POST['athleteName'] ?? '');
if ($athleteName === '') {
    http_response_code(400);
    echo 'Missing athleteName';
    exit;
}

// Allow letters, numbers, spaces, underscores, and hyphens only.
$athleteName = preg_replace('/[^\p{L}\p{N}\s_-]/u', '', $athleteName);

$scriptPath = __DIR__ . DIRECTORY_SEPARATOR . 'test2.py';
$escapedScript = escapeshellarg($scriptPath);
$escapedName = escapeshellarg($athleteName);

// Use Windows start command so the Python script opens separately and returns immediately.
// Change to the script directory first to ensure relative paths work correctly.
$command = "cmd /C cd " . escapeshellarg(__DIR__) . " && start \"\" python $escapedScript $escapedName";
$output = shell_exec($command);

http_response_code(200);
echo "Started test2.py for $athleteName";
