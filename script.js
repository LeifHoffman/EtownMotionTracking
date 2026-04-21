// Get chart canvas elements and contexts if they exist
const jumpCanvas = document.getElementById('jumpChart');
const dashCanvas = document.getElementById('dashChart');
const jumpCtx = jumpCanvas ? jumpCanvas.getContext('2d') : null;
const dashCtx = dashCanvas ? dashCanvas.getContext('2d') : null;

// Data for charts
const jumpData = [14.5, 14.8, 15.2, 15.1, 15.6, 15.9, 16.3, 16.8, 17.1, 17.5, 18.2];
const dashData = [4.45, 4.42, 4.38, 4.40, 4.35, 4.37, 4.42, 4.38, 4.35, 4.30, 4.33];
const months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'];

// Function to draw line chart
function drawLineChart(ctx, data, labels, minY, maxY) {
    const canvas = ctx.canvas;
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Calculate scales
    const xStep = chartWidth / (data.length - 1);
    const yRange = maxY - minY;
    const yScale = chartHeight / yRange;

    // Draw grid lines
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }

    // Draw Y-axis labels
    ctx.fillStyle = '#999';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
        const value = maxY - (yRange / 5) * i;
        const y = padding + (chartHeight / 5) * i;
        ctx.fillText(value.toFixed(1), padding - 10, y + 4);
    }

    // Draw X-axis labels
    ctx.textAlign = 'center';
    labels.forEach((label, i) => {
        if (i % 2 === 0) {
            const x = padding + xStep * i;
            ctx.fillText(label, x, height - 15);
        }
    });

    // Draw line
    ctx.strokeStyle = '#1d1d1f';
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((value, i) => {
        const x = padding + xStep * i;
        const y = padding + chartHeight - ((value - minY) * yScale);
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();

    // Draw points
    ctx.fillStyle = '#1d1d1f';
    data.forEach((value, i) => {
        const x = padding + xStep * i;
        const y = padding + chartHeight - ((value - minY) * yScale);
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });
}

// Function to resize canvases and redraw charts
function resizeCanvases() {
    document.querySelectorAll('canvas').forEach(canvas => {
        const container = canvas.parentElement;
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
    });
    
    // Redraw charts with data if the contexts exist
    if (jumpCtx) {
        drawLineChart(jumpCtx, jumpData, months, 13, 19);
    }
    if (dashCtx) {
        drawLineChart(dashCtx, dashData, months, 4.2, 4.5);
    }
}

// --- run button recording action ---
const runButton = document.getElementById('run');
if (runButton) {
    runButton.addEventListener('click', async () => {
        const athleteSelect = document.getElementById('athleteSelect');
        if (!athleteSelect || !athleteSelect.value) {
            alert('Please select an athlete first.');
            return;
        }

        const athleteName = athleteSelect.options[athleteSelect.selectedIndex].text.trim();
        if (!athleteName) {
            alert('Selected athlete has no valid name.');
            return;
        }

        runButton.disabled = true;
        const originalText = runButton.textContent;
        runButton.textContent = 'Starting...';

        try {
            const formData = new FormData();
            formData.append('athleteName', athleteName);

            const response = await fetch('runsavetest.php', {
                method: 'POST',
                body: formData,
            });

            const text = await response.text();
            if (!response.ok) {
                throw new Error(text || 'Failed to start recording script.');
            }
        } catch (error) {
            console.error(error);
            alert('Error starting recording: ' + error.message);
        } finally {
            runButton.disabled = false;
            runButton.textContent = originalText;
        }
    });
}

// Initial draw and setup resize listener
if (jumpCtx || dashCtx) {
    window.addEventListener('resize', resizeCanvases);
    resizeCanvases();
}
