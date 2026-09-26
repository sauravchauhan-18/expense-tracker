// Draw the dashboard charts with the browser's built-in canvas tools.

function prepareCanvas(canvas, height) {
    const width = canvas.clientWidth;
    const pixelRatio = window.devicePixelRatio || 1;

    canvas.style.height = `${height}px`;
    canvas.width = width * pixelRatio;
    canvas.height = height * pixelRatio;

    const context = canvas.getContext("2d");
    context.scale(pixelRatio, pixelRatio);

    return { context, width, height };
}

function drawMonthlyChart() {
    const canvas = document.getElementById("monthly-chart");
    if (!canvas) return;

    const income = Number(canvas.dataset.income);
    const expenses = Number(canvas.dataset.expenses);
    const { context, width, height } = prepareCanvas(canvas, 240);
    const values = [income, expenses];
    const labels = ["Income", "Expenses"];
    const colors = ["#39885a", "#d45b52"];
    const maximum = Math.max(...values, 1);
    const baseline = height - 38;
    const chartHeight = height - 82;
    const barWidth = Math.min(72, width / 5);

    context.font = "13px Arial";
    context.textAlign = "center";
    context.strokeStyle = "#dce2ec";
    context.beginPath();
    context.moveTo(20, baseline);
    context.lineTo(width - 20, baseline);
    context.stroke();

    values.forEach((value, index) => {
        const center = width * (index === 0 ? 0.32 : 0.68);
        const barHeight = (value / maximum) * chartHeight;
        const barTop = baseline - barHeight;

        context.fillStyle = colors[index];
        context.fillRect(center - barWidth / 2, barTop, barWidth, barHeight);
        context.fillStyle = "#17233b";
        context.fillText(value.toFixed(2), center, Math.max(16, barTop - 7));
        context.fillText(labels[index], center, height - 14);
    });
}

function drawCategoryChart() {
    const canvas = document.getElementById("category-chart");
    if (!canvas) return;

    const items = window.expenseByCategory || [];
    const height = Math.max(180, items.length * 34 + 30);
    const { context, width } = prepareCanvas(canvas, height);

    if (items.length === 0) {
        context.fillStyle = "#69758a";
        context.font = "14px Arial";
        context.textAlign = "center";
        context.fillText("No expense entries this month yet", width / 2, height / 2);
        return;
    }

    const labelWidth = Math.min(120, Math.max(82, width * 0.32));
    const chartWidth = Math.max(20, width - labelWidth - 58);
    const maximum = Math.max(...items.map((item) => Number(item.total)), 1);

    context.font = "12px Arial";
    items.forEach((item, index) => {
        const y = 18 + index * 34;
        const amount = Number(item.total);
        const barWidth = (amount / maximum) * chartWidth;
        const label = item.category.length > 16
            ? `${item.category.slice(0, 15)}…`
            : item.category;

        context.fillStyle = "#59657a";
        context.textAlign = "right";
        context.fillText(label, labelWidth - 10, y + 13);

        context.fillStyle = "#5268c9";
        context.fillRect(labelWidth, y, barWidth, 18);

        context.fillStyle = "#17233b";
        context.textAlign = "left";
        context.fillText(amount.toFixed(2), labelWidth + barWidth + 6, y + 13);
    });
}

function drawCharts() {
    drawMonthlyChart();
    drawCategoryChart();
}

drawCharts();
window.addEventListener("resize", drawCharts);
