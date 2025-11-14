// Get canvas contexts
const jumpCtx = document.getElementById('jumpChart').getContext('2d');
const dashCtx = document.getElementById('dashChart').getContext('2d');

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
    
    // Redraw charts with data
    drawLineChart(jumpCtx, jumpData, months, 13, 19);
    drawLineChart(dashCtx, dashData, months, 4.2, 4.5);
}

// Initial draw and setup resize listener
window.addEventListener('resize', resizeCanvases);
resizeCanvases();