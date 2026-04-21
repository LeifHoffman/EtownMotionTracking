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

// ---------------------------
// OPTION 1: Run locally
// ---------------------------

// Absolute paths on the machine where PHP runs:
$python = '/home/team9/EtownMotionTracking/env/bin/python';
$script = '/home/team9/EtownMotionTracking/savetest.py';

// Build command: /path/to/python /path/to/savetest.py "Athlete Name" 2>&1
$cmd = escapeshellarg($python) . ' ' .
       escapeshellarg($script) . ' ' .
       escapeshellarg($athleteName) . ' 2>&1';

// Log what we are running (to webserver error log)
error_log("Running command: " . $cmd);

// Execute
$output = shell_exec($cmd);
error_log("Command output: " . $output);

// ---------------------------
// OPTION 2: Run on Pi via SSH
// Uncomment and adjust if PHP is on a different host.
// ---------------------------
/*
$remotePython = '/home/team9/EtownMotionTracking/env/bin/python';
$remoteScript = '/home/team9/EtownMotionTracking/savetest.py';

$remoteCmd = escapeshellarg($remotePython) . ' ' .
             escapeshellarg($remoteScript) . ' ' .
             escapeshellarg($athleteName);

// SSH user@host for the Pi
$sshUserHost = 'team9@PI_HOST_OR_IP';

// ssh 'user@host' 'remote_python remote_script "name"' 2>&1
$cmd = 'ssh ' . escapeshellarg($sshUserHost) . ' ' . escapeshellarg($remoteCmd) . ' 2>&1';

error_log("Running SSH command: " . $cmd);
$output = shell_exec($cmd);
error_log("SSH output: " . $output);
*/

http_response_code(200);
echo "Started savetest.py for " . htmlspecialchars($athleteName, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');