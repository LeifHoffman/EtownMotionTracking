<?php
// Database connection
$db = new PDO('sqlite:motion_tracking.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Fetch athletes
$athletes = [];
try {
    $stmt = $db->query('SELECT id, name FROM athletes ORDER BY name');
    $athletes = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    error_log('Error fetching athletes: ' . $e->getMessage());
}

// Fetch sessions
$sessions = [];
try {
    $stmt = $db->query('
        SELECT 
            s.id,
            a.name as athlete_name,
            s.started_at,
            s.session_type,
            COALESCE(
                (SELECT metric_value FROM results WHERE session_id = s.id LIMIT 1),
                NULL
            ) as metric_value
        FROM sessions s
        JOIN athletes a ON s.athlete_id = a.id
        ORDER BY a.name, s.started_at DESC
    ');
    $sessions = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    error_log('Error fetching sessions: ' . $e->getMessage());
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elizabethtown College Athletics</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>

    <!-- HEADER -->
    <div class="header">
        <h1>Elizabethtown College Athletics</h1>
    </div>

    <!-- NAV -->
    <div class="nav">
        <button onclick="window.location.href='home.php';" class="button-active">
            Recording
        </button>
        <button onclick="window.location.href='stats.php';">
            Stats
        </button>
    </div>

    <!-- MAIN CONTENT -->
    <div class="container">

        <!-- SELECT ATHLETE + START RECORDING -->
        <div class="home-action-grid">

            <div class="action-card" id="selectAthleteCard">
                <div class="action-card-label">Select Athlete</div>
                <select id="athleteSelect" class="athlete-select">
                    <?php foreach ($athletes as $athlete): ?>
                        <option value="<?php echo htmlspecialchars($athlete['id']); ?>">
                            <?php echo htmlspecialchars($athlete['name']); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

            <button id="run" class="start-btn">Start Recording</button>

        </div>

        <!-- SESSION HISTORY -->
        <div class="table-card">
            <div class="chart-title">Session History</div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Athlete</th>
                        <th>Date</th>
                        <th>Test</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody id="sessionTableBody">
                    <?php if (empty($sessions)): ?>
                        <tr><td colspan="4" style="color:#999; text-align:center; padding:20px;">No sessions recorded yet.</td></tr>
                    <?php else: ?>
                        <?php foreach ($sessions as $session): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($session['athlete_name']); ?></td>
                                <td><?php echo htmlspecialchars(explode('T', $session['started_at'])[0]); ?></td>
                                <td>Vertical Jump</td>
                                <td>
                                    <?php 
                                        if ($session['metric_value'] !== null) {
                                            echo htmlspecialchars(number_format($session['metric_value'], 2)) . ' in';
                                        } else {
                                            echo '—';
                                        }
                                    ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

    </div>

    <script src="script.js"></script>
    <script>
        const athleteSelect = document.getElementById('athleteSelect');
        const runBtn = document.getElementById('run');

        function updateRunButtonState() {
            if (athleteSelect && athleteSelect.value) {
                runBtn.disabled = false;
                runBtn.classList.add('start-btn-ready');
            } else {
                runBtn.disabled = true;
                runBtn.classList.remove('start-btn-ready');
            }
        }

        if (athleteSelect) {
            athleteSelect.addEventListener('change', updateRunButtonState);
            updateRunButtonState();
        }
    </script>

</body>
</html>
