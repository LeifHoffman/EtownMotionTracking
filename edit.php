<?php
// edit.php — Athlete Database Editor

// Database connection
$db = new PDO('sqlite:motion_tracking.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Ensure the athletes table exists (in case it wasn't created yet)
$db->exec("CREATE TABLE IF NOT EXISTS athletes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)");

$message = '';

// Handle form submissions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action'])) {
        if ($_POST['action'] === 'add' && !empty(trim($_POST['name']))) {
            $stmt = $db->prepare("INSERT INTO athletes (name) VALUES (:name)");
            $stmt->execute([':name' => trim($_POST['name'])]);
            $message = 'Athlete added successfully.';
        } elseif ($_POST['action'] === 'delete' && isset($_POST['id'])) {
            $stmt = $db->prepare("DELETE FROM athletes WHERE id = :id");
            $stmt->execute([':id' => (int)$_POST['id']]);
            $message = 'Athlete removed successfully.';
        }
    }
}

// Fetch all athletes
$athletes = $db->query("SELECT id, name FROM athletes ORDER BY name")->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Athletes - Elizabethtown College Athletics</title>
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
        <button onclick="window.location.href='stats.php';">
            Stats
        </button>
        <button onclick="window.location.href='edit.php';" class="button-active">
            Edit Athletes
        </button>
    </div>

    <!-- MAIN CONTENT -->
    <div class="container">

        <!-- Message Display -->
        <?php if ($message): ?>
            <div class="message-box message-success">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>

        <!-- Add Athlete Form -->
        <div class="table-card" style="margin-bottom: 32px;">
            <div class="chart-title">Add Table Information</div>

            <!-- Centered input and button -->
            <div style="text-align: center; margin: 20px 0;">
                <form method="POST" class="athlete-form">
                    <input type="hidden" name="action" value="add">

                    <div style="margin-bottom: 15px;">
                        <label for="athleteName">Athlete Name</label><br>
                        <input
                            type="text"
                            id="athleteName"
                            name="name"
                            placeholder="???"
                            required
                            style="padding: 5px; width: 250px; font-size: 1rem; text-align: center; margin-top: 10px;"
                        >
                    </div>

                    <div>
                        <button
                            type="submit"
                            id="addAthleteBtn"
                            class="start-btn"
                            disabled
                            style="padding: 10px 20px; font-size: 1rem; cursor: not-allowed;"
                        >
                            Add
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Current Athletes List -->
        <div class="table-card">
            <div class="chart-title">Current Athletes</div>

            <?php if (empty($athletes)): ?>
                <p class="empty-state" style="text-align: center;">
                    No athletes found. Add some athletes above.
                </p>
            <?php else: ?>
                <table class="data-table" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Athlete Name</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($athletes as $index => $athlete): ?>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 12px; text-align: left;">
                                    <?php echo $index + 1; ?>
                                </td>
                                <td style="padding: 12px;">
                                    <?php echo htmlspecialchars($athlete['name']); ?>
                                </td>
                                <td style="padding: 12px; text-align: left;">
                                    <form
                                        method="POST"
                                        class="delete-form"
                                        onsubmit="return confirm('Are you sure you want to delete <?php echo htmlspecialchars($athlete['name'], ENT_QUOTES); ?>? This action cannot be undone.');"
                                    >
                                        <input type="hidden" name="action" value="delete">
                                        <input type="hidden" name="id" value="<?php echo $athlete['id']; ?>">
                                        <button
                                            type="submit"
                                            class="btn-danger"
                                            style="padding: 6px 12px; font-size: 0.9rem;"
                                        >
                                            Delete
                                        </button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </div>

    </div>

    <script>
        const athleteNameInput = document.getElementById('athleteName');
        const addAthleteBtn = document.getElementById('addAthleteBtn');

        function updateAddButtonState() {
            const hasText = athleteNameInput && athleteNameInput.value.trim() !== '';

            addAthleteBtn.disabled = !hasText;

            if (hasText) {
                addAthleteBtn.classList.add('start-btn-ready');
            } else {
                addAthleteBtn.classList.remove('start-btn-ready');
            }
        }

        if (athleteNameInput) {
            athleteNameInput.addEventListener('input', updateAddButtonState);
            // Initial state on page load
            updateAddButtonState();
        }
    </script>

</body>
</html>