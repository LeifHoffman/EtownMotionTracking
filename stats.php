<?php
// Database connection
$db = new PDO('sqlite:motion_tracking.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Fetch top performers (athletes with best single jump result)
$topPerformers = [];
try {
    $stmt = $db->query('
        SELECT 
            a.name,
            MAX(r.metric_value) as best_jump
        FROM athletes a
        LEFT JOIN sessions s ON a.id = s.athlete_id
        LEFT JOIN results r ON s.id = r.session_id
        WHERE r.metric_value IS NOT NULL
        GROUP BY a.id
        ORDER BY best_jump DESC
        LIMIT 5
    ');
    $topPerformers = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    error_log('Error fetching top performers: ' . $e->getMessage());
}

// Calculate average jump for all athletes
$avgJump = 0;
try {
    $stmt = $db->query('
        SELECT AVG(metric_value) as avg_value
        FROM results
        WHERE metric_name = "vertical_jump" OR metric_name IS NULL
    ');
    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    $avgJump = $result['avg_value'] ?? 0;
} catch (Exception $e) {
    error_log('Error calculating average: ' . $e->getMessage());
}
?>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elizabethtown College Athletics - Stats</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>

    <!-- HEADER -->
    <div class="header">
        <h1>Elizabethtown College Athletics</h1>
    </div>

    <!-- NAV -->
    <div class="nav">
        <button onclick="window.location.href='home.php';">
            Recording
        </button>
        <button onclick="window.location.href='stats.php';" class="button-active">
            Stats
        </button>
    </div>

    <!-- MAIN CONTENT -->
    <div class="container">

        <!-- Jump Results Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Average Vertical Jump (in)</div>
                <div class="metric-value"><?php echo number_format($avgJump, 1); ?></div>
                <div class="metric-change">Based on recorded sessions</div>
            </div>
        </div>

        <!-- Top Performers + Jump Chart -->
        <div class="content-grid">
            <div class="chart-card">
                <div class="chart-title">Average Jump Heights for All Athletes (Monthly)</div>
                <div class="chart-container">
                    <canvas id="jumpChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-title">Top Performers: Vertical Jump</div>
                <ul class="performers-list">
                    <?php if (!empty($topPerformers)): ?>
                        <?php foreach ($topPerformers as $performer): ?>
                            <li class="performer-item">
                                <div class="performer-avatar"></div>
                                <div class="performer-info">
                                    <div class="performer-name">
                                        <?php echo htmlspecialchars($performer['name']); ?> - 
                                        <?php echo number_format($performer['best_jump'], 1); ?> in
                                    </div>
                                </div>
                            </li>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <li class="performer-item" style="color: #999;">
                            No performance data available yet
                        </li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>

        <!-- Jump Totals Table -->
        <div class="bottom-grid-stats">
            <div class="table-card">
                <div class="chart-title">Session Count by Athlete</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Athlete</th>
                            <th>Sessions</th>
                            <th>Best Jump</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php 
                        try {
                            $stmt = $db->query('
                                SELECT 
                                    a.name,
                                    COUNT(s.id) as session_count,
                                    MAX(r.metric_value) as best_jump
                                FROM athletes a
                                LEFT JOIN sessions s ON a.id = s.athlete_id
                                LEFT JOIN results r ON s.id = r.session_id
                                GROUP BY a.id
                                ORDER BY session_count DESC
                            ');
                            $athleteStats = $stmt->fetchAll(PDO::FETCH_ASSOC);
                            
                            if (!empty($athleteStats)) {
                                foreach ($athleteStats as $stat) {
                                    echo '<tr>';
                                    echo '<td>' . htmlspecialchars($stat['name']) . '</td>';
                                    echo '<td>' . htmlspecialchars($stat['session_count']) . '</td>';
                                    echo '<td>' . ($stat['best_jump'] ? number_format($stat['best_jump'], 1) . ' in' : '—') . '</td>';
                                    echo '</tr>';
                                }
                            } else {
                                echo '<tr><td colspan="3" style="color:#999; text-align:center;">No data available</td></tr>';
                            }
                        } catch (Exception $e) {
                            echo '<tr><td colspan="3" style="color:#999; text-align:center;">Error loading data</td></tr>';
                        }
                        ?>
                    </tbody>
                </table>
            </div>

            <!-- Export placeholder -->
            <div class="chart-card export-card">
                <div class="chart-title">Database Export</div>
                <p class="export-desc">Download a copy of all recorded session data.</p>
                <button class="export-btn" disabled title="Coming soon">Export Database</button>
            </div>
        </div>

    </div>

    <script src="script.js"></script>

</body>
</html>
