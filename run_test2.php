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
$command = "cmd /C start \"\" python $escapedScript $escapedName";

// If python is not available, try the py launcher.
$output = shell_exec($command);
if ($output === null) {
    $command = "cmd /C start \"\" py $escapedScript $escapedName";
    $output = shell_exec($command);
}

if ($output === null) {
    http_response_code(500);
    echo 'Unable to launch Python process. Ensure Python is installed and on the PATH.';
    exit;
}

http_response_code(200);
echo "Started test2.py for $athleteName";
