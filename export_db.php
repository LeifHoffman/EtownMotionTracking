<?php
// export_db.php — Export entire motion_tracking.db in a CSV that Excel can open

// Database connection (same as other pages)
$db = new PDO('sqlite:motion_tracking.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Helper to dump a table as CSV section
function exportTableSection($output, $db, $title, $query) {
    // Section title row (blank line before, except at start)
    fputcsv($output, ['']);
    fputcsv($output, [$title]);

    // Run query
    $stmt = $db->query($query);
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    if (empty($rows)) {
        fputcsv($output, ['(no rows)']);
        return;
    }

    // Header row
    fputcsv($output, array_keys($rows[0]));

    // Data rows
    foreach ($rows as $row) {
        fputcsv($output, $row);
    }
}

// Prepare HTTP headers
$filename = 'motion_tracking_export_' . date('Y-m-d_H-i-s') . '.csv';
header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="' . $filename . '"');

// Use output stream
$output = fopen('php://output', 'w');

// Optional first line: export info
fputcsv($output, ['Motion Tracking Database Export', 'Generated at', date('Y-m-d H:i:s')]);

// ATHLETES
exportTableSection(
    $output,
    $db,
    'Table: athletes',
    'SELECT id, name, year, height, weight FROM athletes ORDER BY id'
);

// SESSIONS
exportTableSection(
    $output,
    $db,
    'Table: sessions',
    'SELECT id, athlete_id, started_at, ended_at, frame_count, session_type, video_filename FROM sessions ORDER BY id'
);

// RESULTS
exportTableSection(
    $output,
    $db,
    'Table: results',
    'SELECT id, session_id, metric_name, metric_value FROM results ORDER BY id'
);

fclose($output);
exit;