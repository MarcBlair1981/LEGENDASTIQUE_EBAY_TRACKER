/**
 * Legendastique Collectibles - Main Logic (API Version)
 * App Version: 5 (Production)
 */

// --- State Management ---
const state = {
    items: [],
    currentView: 'dashboard'
};

async function loadState() {
    try {
        const response = await fetch(`/api/items?_t=${Date.now()}`);
        const data = await response.json();
        state.items = data.items || [];
        render();
        updateDebugBar();
    } catch (error) {
        console.error("Failed to load items:", error);
        document.getElementById('debug-bar').textContent = "Error loading items: " + error.message;
    }
}

async function syncItem(item) {
    try {
        const response = await fetch(`/api/items/${item.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
        });
        if (!response.ok) throw new Error('Update failed');
        await loadState();
    } catch (e) {
        console.error(e);
        alert("Failed to save changes to server.");
    }
}

// --- DOM Elements ---
const elements = {
    navDashboard: document.getElementById('nav-dashboard'),
    navActivity: document.getElementById('nav-activity'),
    dashboardView: document.getElementById('dashboard-view'),
    activityView: document.getElementById('activity-view'),
    activityListBody: document.getElementById('activity-list-body'),

    totalValue: document.getElementById('total-value'),
    totalItems: document.getElementById('total-items'),
    itemsList: document.getElementById('items-list'),
    chartContainer: document.getElementById('chart-container'),
    lastCheckTime: document.getElementById('last-check-time'),
    checkPricesBtn: document.getElementById('check-prices-btn'),
    checkPricesLabel: document.getElementById('check-prices-label'),

    addItemBtn: document.getElementById('add-item-btn'),
    addItemModal: document.getElementById('add-item-modal'),
    closeModalBtn: document.getElementById('close-modal-btn'),
    addItemForm: document.getElementById('add-item-form'),
    itemNameInput: document.getElementById('item-name'),
    itemCategoryInput: document.getElementById('item-category'),
    itemPriceInput: document.getElementById('item-price'),

    updatePriceModal: document.getElementById('update-price-modal'),
    closeUpdateBtn: document.getElementById('close-update-btn'),
    updatePriceForm: document.getElementById('update-price-form'),
    updateItemLabel: document.getElementById('update-item-label'),
    updateItemPrice: document.getElementById('update-item-price'),
    updateItemId: document.getElementById('update-item-id'),

    historyModal: document.getElementById('history-modal'),
    closeHistoryBtn: document.getElementById('close-history-btn'),
    historyModalTitle: document.getElementById('history-modal-title'),
    addHistoryForm: document.getElementById('add-history-form'),
    historyDateInput: document.getElementById('history-date'),
    historyPriceInput: document.getElementById('history-price'),
    historyListBody: document.getElementById('history-list-body'),
    itemHistoryChartContainer: document.getElementById('item-history-chart'),

    modalBackdrop: document.getElementById('modal-backdrop'),
    searchInput: document.getElementById('search-input'),
};

let currentEditingItemId = null;

// --- Utilities ---
const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(num);
};

const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};

// --- Chart Helpers ---
function createSvgChart(container, dataPoints, heightOverride = null) {
    container.innerHTML = '';
    if (!dataPoints || dataPoints.length === 0) {
        container.innerHTML = '<div class="flex items-center justify-center p-4 text-muted" style="height:100%">No data available</div>';
        return;
    }
    if (dataPoints.length === 1) dataPoints = [dataPoints[0], dataPoints[0]];
    const width = container.clientWidth;
    const height = heightOverride || container.clientHeight;
    const padding = { top: 20, right: 20, bottom: 30, left: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const maxVal = Math.max(...dataPoints.map(d => d.value)) * 1.05;
    const minVal = Math.min(...dataPoints.map(d => d.value)) * 0.95;
    const getX = (index) => padding.left + (index / (dataPoints.length - 1)) * chartWidth;
    const getY = (val) => padding.top + chartHeight - ((val - minVal) / (maxVal - minVal || 1)) * chartHeight;
    const svgNs = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNs, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

    // Gradient
    const defs = document.createElementNS(svgNs, "defs");
    const uniqueId = "grad-" + Math.random().toString(36).substr(2, 9);
    const gradient = document.createElementNS(svgNs, "linearGradient");
    gradient.id = uniqueId;
    gradient.innerHTML = `<stop offset="0%" stop-color="#3b82f6" stop-opacity="0.5"/><stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>`;
    defs.appendChild(gradient);
    svg.appendChild(defs);

    let pathD = `M ${getX(0)} ${getY(dataPoints[0].value)}`;
    dataPoints.forEach((d, i) => { pathD += ` L ${getX(i)} ${getY(d.value)}`; });
    const areaD = `${pathD} L ${getX(dataPoints.length - 1)} ${height - padding.bottom} L ${getX(0)} ${height - padding.bottom} Z`;

    const areaPath = document.createElementNS(svgNs, "path");
    areaPath.setAttribute("d", areaD);
    areaPath.setAttribute("fill", `url(#${uniqueId})`);
    areaPath.setAttribute("opacity", "0.2");
    svg.appendChild(areaPath);

    const linePath = document.createElementNS(svgNs, "path");
    linePath.setAttribute("d", pathD);
    linePath.setAttribute("stroke", "#3b82f6");
    linePath.setAttribute("stroke-width", "3");
    linePath.setAttribute("fill", "none");
    svg.appendChild(linePath);

    // Axes
    const numYLabels = 5;
    for (let i = 0; i < numYLabels; i++) {
        const val = minVal + (i * ((maxVal - minVal) / (numYLabels - 1)));
        const yFn = getY(val);
        const text = document.createElementNS(svgNs, "text");
        text.setAttribute("x", padding.left - 10);
        text.setAttribute("y", yFn + 4);
        text.setAttribute("text-anchor", "end");
        text.setAttribute("fill", "var(--text-muted)");
        text.setAttribute("font-size", "10");
        text.textContent = (val >= 1000) ? `£${(val / 1000).toFixed(1)}k` : `£${val.toFixed(0)}`;
        svg.appendChild(text);
        const grid = document.createElementNS(svgNs, "line");
        grid.setAttribute("x1", padding.left);
        grid.setAttribute("y1", yFn);
        grid.setAttribute("x2", width - padding.right);
        grid.setAttribute("y2", yFn);
        grid.setAttribute("stroke", "var(--card-border)");
        grid.setAttribute("stroke-dasharray", "4 4");
        svg.appendChild(grid);
    }

    container.appendChild(svg);
}

// --- Rendering Logic ---
function render() {
    if (state.currentView === 'activity') {
        elements.dashboardView.classList.add('hidden');
        elements.activityView.classList.remove('hidden');
        renderActivityFeed();
        elements.navDashboard.classList.remove('text-accent');
        elements.navDashboard.classList.add('text-muted');
        elements.navActivity.classList.add('text-accent');
        elements.navActivity.classList.remove('text-muted');
    } else {
        elements.dashboardView.classList.remove('hidden');
        elements.activityView.classList.add('hidden');
        renderDashboard();
        elements.navDashboard.classList.add('text-accent');
        elements.navDashboard.classList.remove('text-muted');
        elements.navActivity.classList.remove('text-accent');
        elements.navActivity.classList.add('text-muted');
    }
}

/* Sparkline Generator */
function getSparkline(history) {
    if (!history || history.length < 2) return '';

    // Sort by date
    const sorted = [...history].sort((a, b) => new Date(a.date) - new Date(b.date));
    // Take last 7 points or all if less
    const points = sorted.slice(-10);

    const min = Math.min(...points.map(p => p.price));
    const max = Math.max(...points.map(p => p.price));
    const range = max - min || 1; // Avoid divide by zero

    const width = 120;
    const height = 30;

    // Generate path
    let d = `M 0 ${height - ((points[0].price - min) / range * height)}`;
    points.forEach((p, i) => {
        const x = (i / (points.length - 1)) * width;
        const y = height - ((p.price - min) / range * height);
        d += ` L ${x} ${y}`;
    });

    return `<svg class="sparkline-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <path class="sparkline-path" d="${d}" />
    </svg>`;
}

function renderChart() {
    const allHistory = [];
    state.items.forEach(item => {
        if (item.priceHistory) {
            item.priceHistory.forEach(h => {
                allHistory.push({ date: new Date(h.date).getTime(), price: h.price, itemId: item.id });
            });
        }
    });

    if (allHistory.length === 0) {
        elements.chartContainer.innerHTML = '<div class="flex items-center justify-center p-4 text-muted" style="height:100%">No history data</div>';
        return;
    }

    // specific dates to plot (sorted unique dates)
    const uniqueDates = [...new Set(allHistory.map(h => h.date))].sort((a, b) => a - b);

    // Create data points
    const dataPoints = uniqueDates.map(date => {
        let total = 0;
        state.items.forEach(item => {
            // Find latest price for this item at or before 'date'
            // If item has no history before this date, use 0 or acquisition cost? Let's use 0.
            if (item.priceHistory) {
                const relevantHistory = item.priceHistory
                    .filter(h => new Date(h.date).getTime() <= date)
                    .sort((a, b) => new Date(b.date) - new Date(a.date)); // desc

                if (relevantHistory.length > 0) {
                    total += relevantHistory[0].price;
                }
            }
        });
        return { value: total, date: date };
    });

    createSvgChart(elements.chartContainer, dataPoints);
}

function renderDashboard() {
    const searchTerm = elements.searchInput.value.toLowerCase();
    const filteredItems = state.items.filter(item =>
        (item.name && item.name.toLowerCase().includes(searchTerm)) ||
        (item.category && item.category.toLowerCase().includes(searchTerm))
    );

    const totalVal = state.items.reduce((sum, item) => sum + Number(item.price || 0), 0);
    elements.totalValue.textContent = formatCurrency(totalVal);
    elements.totalItems.textContent = state.items.length;

    // Last Check Logic
    let lastCheck = null;
    state.items.forEach(item => {
        if (item.priceHistory) {
            item.priceHistory.forEach(h => {
                const date = new Date(h.date);
                if (!lastCheck || date > lastCheck) lastCheck = date;
            });
        }
    });
    const now = new Date();
    if (lastCheck) {
        const timeStr = lastCheck.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        if (lastCheck.toDateString() === now.toDateString()) elements.lastCheckTime.textContent = `Today at ${timeStr}`;
        else elements.lastCheckTime.textContent = `${lastCheck.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} at ${timeStr}`;
    } else {
        elements.lastCheckTime.textContent = "Never";
    }

    try {
        renderChart();
    } catch (e) {
        console.error("Chart render failed:", e);
        elements.chartContainer.innerHTML = '<div class="text-danger p-4">Chart Error</div>';
    }

    elements.itemsList.innerHTML = '';

    if (filteredItems.length === 0) {
        elements.itemsList.innerHTML = `<div style="padding: 24px; text-align: center; color: #666;">No items found matching "${searchTerm}".</div>`;
        return;
    }

    filteredItems.forEach(item => {
        const category = item.category || 'Uncategorized';
        const excludeBadges = item.excludeKeywords ? item.excludeKeywords.split(',').map(w => `<span class="exclude-badge">-${w.trim()}</span>`).join(' ') : '';
        const sparkline = getSparkline(item.priceHistory);

        // Calculate Trend (Last v First in history or Last v Prev)
        let trend = '';
        if (item.priceHistory && item.priceHistory.length > 1) {
            const current = item.price;
            const prev = item.priceHistory[item.priceHistory.length - 2].price;
            const diff = current - prev;
            const pct = (diff / prev) * 100;
            const color = diff > 0 ? '#10b981' : (diff < 0 ? '#ef4444' : '#64748b');
            const arrow = diff > 0 ? '▲' : (diff < 0 ? '▼' : '▬');
            trend = `<span style="color:${color}; font-size:11px; font-weight:600;">${arrow} ${Math.abs(pct).toFixed(1)}%</span>`;
        } else {
            trend = `<span style="color:#64748b; font-size:11px;">-</span>`;
        }

        const row = document.createElement('div');
        row.className = 'ticker-row';
        row.innerHTML = `
            <div class="item-name-cell">
                <span class="item-name-main">${item.name}</span>
                <div class="item-meta">
                    <span class="tag-badge">${category}</span>
                    ${excludeBadges}
                </div>
            </div>
            
            <div class="price-cell">${formatCurrency(item.price || 0)}</div>
            
            <div class="chart-cell">
                ${sparkline}
            </div>
            
            <div style="display:flex; align-items:center;">
                ${trend}
            </div>
            
            <div style="font-size: 11px; color: #888;">
                ${item.priceHistory && item.priceHistory.length > 0 ? new Date(item.priceHistory[item.priceHistory.length - 1].date).toLocaleDateString() : '-'}
            </div>
            
            <div>
                 ${item.activeListingUrl
                ? `<a href="${item.activeListingUrl}" target="_blank" style="color: #3b82f6; font-size: 12px; text-decoration: none;">View ↗</a>`
                : `<span style="color: #444; font-size: 12px;">-</span>`}
            </div>
            
            <div class="ticker-actions" style="gap: 4px;">
                <button id="check-btn-${item.id}" class="btn-icon" onclick="checkItemPrice(${item.id})" title="Check Price Now" style="color: #3b82f6;">↻</button>
                <button class="btn-icon" onclick="openEditModal(${item.id})" title="Edit Settings">⚙</button>
                <button class="btn-icon" onclick="openHistoryModal(${item.id})" title="View History">📅</button>
                <button class="btn-icon" onclick="deleteItem(${item.id})" title="Delete Item" style="color: #ef4444;">✕</button>
            </div>
        `;
        elements.itemsList.appendChild(row);
    });
}

// --- Stats Toggle Logic (Moved from renderDashboard) ---
// --- Stats Toggle Logic (Moved to bottom) ---
// elements.toggleStatsBtn = document.getElementById('toggle-stats-btn');
// elements.statsSection = document.getElementById('stats-section');
// let statsVisible = true;

if (elements.toggleStatsBtn) {
    elements.toggleStatsBtn.addEventListener('click', () => {
        statsVisible = !statsVisible;
        if (statsVisible) {
            elements.statsSection.style.maxHeight = '500px'; // Arbitrary large enough height
            elements.statsSection.style.opacity = '1';
            elements.statsSection.style.marginBottom = '24px';
            elements.toggleStatsBtn.textContent = "Hide Stats ▲";
        } else {
            elements.statsSection.style.maxHeight = '0';
            elements.statsSection.style.opacity = '0';
            elements.statsSection.style.marginBottom = '0';
            elements.toggleStatsBtn.textContent = "Show Stats ▼";
        }
    });
}

window.checkItemPrice = async function (id) {
    console.log(`Checking price for item ID: ${id}`);
    const btn = document.getElementById(`check-btn-${id}`);
    if (btn) {
        btn.classList.add('spinning');
        btn.textContent = '...';
        btn.disabled = true;
    }

    try {
        console.log(`Fetching: /api/items/${id}/check`);
        const res = await fetch(`/api/items/${id}/check`, { method: 'POST' });
        console.log(`Response status: ${res.status}`);

        const result = await res.json();
        console.log('Result:', result);

        if (result.status === 'success') {
            console.log(`Price updated: £${result.price}`);
        } else {
            console.error('Check failed:', result);
            alert(`Check failed: ${result.status}`);
        }
    } catch (e) {
        console.error('Error checking price:', e);
        alert(`Error checking price: ${e.message}`);
    } finally {
        await loadState();
    }
};

function renderActivityFeed() {
    const salesEvents = [];
    state.items.forEach(item => {
        if (item.priceHistory) {
            item.priceHistory.forEach(h => {
                salesEvents.push({
                    item: item.name,
                    date: h.date,
                    price: h.price,
                    url: h.url
                });
            });
        }
    });
    salesEvents.sort((a, b) => new Date(b.date) - new Date(a.date));
    elements.activityListBody.innerHTML = '';

    if (salesEvents.length === 0) {
        elements.activityListBody.innerHTML = '<tr><td colspan="4" class="p-4 text-center">No activity.</td></tr>';
        return;
    }

    salesEvents.forEach(event => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--card-border)';
        let sourceCell = '<span class="text-muted">-</span>';
        if (event.url) {
            sourceCell = `<a href="${event.url}" target="_blank" class="text-accent" style="text-decoration: underline;">View Listing</a>`;
        }
        tr.innerHTML = `
            <td style="padding: 12px 8px;">${formatDate(event.date)}</td>
            <td style="padding: 12px 8px; font-weight: 600;">${event.item}</td>
            <td style="padding: 12px 8px;">${formatCurrency(event.price)}</td>
            <td style="padding: 12px 8px;">${sourceCell}</td>
        `;
        elements.activityListBody.appendChild(tr);
    });
}

// (Chart rendering omitted for brevity - it's fine)
function renderItemChart(item) {
    if (!item || !item.priceHistory) return;
    const sortedHistory = [...item.priceHistory].sort((a, b) => new Date(a.date) - new Date(b.date));
    const chartData = sortedHistory.map(h => ({ date: h.date, value: h.price }));
    createSvgChart(elements.itemHistoryChartContainer, chartData);
}

// --- Modals & Actions ---
window.openHistoryModal = function (id) {
    const item = state.items.find(i => i.id === id);
    if (!item) return;
    currentEditingItemId = id;
    elements.historyModalTitle.textContent = `History: ${item.name} `;
    toggleModal(elements.historyModal, true);
    renderHistoryList(item);
    renderItemChart(item);
};

function renderHistoryList(item) {
    elements.historyListBody.innerHTML = '';
    const sortedHistory = [...item.priceHistory].sort((a, b) => new Date(b.date) - new Date(a.date));
    sortedHistory.forEach((record, index) => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--card-border)';

        let linkHtml = '';
        if (record.url) {
            linkHtml = `<a href="${record.url}" target="_blank" title="View Source">🔗</a>`;
        }

        tr.innerHTML = `
            <td style="padding: 12px 8px;">${formatDate(record.date)}</td>
            <td style="padding: 12px 8px;">${formatCurrency(record.price)} ${linkHtml}</td>
            <td style="padding: 12px 8px;"><button class="btn" style="color:red" onclick="deleteHistoryEntry(${index})">Del</button></td>
        `;
        elements.historyListBody.appendChild(tr);
    });
}

window.triggerPriceCheck = async function () {
    const btn = elements.checkPricesBtn;
    const label = elements.checkPricesLabel;
    if (btn.disabled) return;
    btn.disabled = true;
    label.textContent = "⌛ Checking...";
    try {
        const response = await fetch('/api/check-prices', { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            alert(`Check completed: \n\n${result.results.join('\n')} `);
            await loadState();
        } else {
            alert("Failed to check prices.");
        }
    } catch (e) {
        console.error(e);
        alert("Error connecting to server.");
    } finally {
        btn.disabled = false;
        label.textContent = "↻ Check Prices";
    }
};

window.openUpdateModal = function (id) {
    const item = state.items.find(i => i.id === id);
    if (!item) return;
    elements.updateItemId.value = item.id;
    elements.updateItemLabel.textContent = `Update Price: ${item.name} `;
    elements.updateItemPrice.value = item.price;
    toggleModal(elements.updatePriceModal, true);
    setTimeout(() => elements.updateItemPrice.focus(), 100);
};

window.deleteItem = async function (id) {
    if (confirm("Delete item?")) {
        await fetch(`/ api / items / ${id} `, { method: 'DELETE' });
        await loadState();
    }
};

async function updatePrice(e) {
    e.preventDefault();
    const id = parseInt(elements.updateItemId.value);
    const newPrice = parseFloat(elements.updateItemPrice.value);
    await fetch(`/ api / items / ${id} /price`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ price: newPrice, date: new Date().toISOString() }) });
    toggleModal(elements.updatePriceModal, false);
    await loadState();
}

async function addHistoryEntry(e) {
    e.preventDefault();
    if (!currentEditingItemId) return;
    const dateVal = elements.historyDateInput.value;
    const priceVal = parseFloat(elements.historyPriceInput.value);
    const item = state.items.find(i => i.id === currentEditingItemId);
    item.priceHistory.push({ date: new Date(dateVal).toISOString(), price: priceVal });
    // Let backend sort or do it here. Sync item handles it.
    await syncItem(item); // this syncs the whole item object state
    const updatedItem = state.items.find(i => i.id === currentEditingItemId);
    renderItemChart(updatedItem);
    renderHistoryList(updatedItem);
}

async function deleteHistoryEntry(index) {
    // Basic delete implementation via sync
    const item = state.items.find(i => i.id === currentEditingItemId);
    // Sort first to match index
    const sortedHistory = [...item.priceHistory].sort((a, b) => new Date(b.date) - new Date(a.date));
    const toDelete = sortedHistory[index];
    item.priceHistory = item.priceHistory.filter(x => x !== toDelete);
    await syncItem(item);
    const updatedItem = state.items.find(i => i.id === currentEditingItemId);
    renderItemChart(updatedItem);
    renderHistoryList(updatedItem);
}

// Event Listeners
// Event Listeners
elements.addItemBtn.addEventListener('click', () => {
    openAddModal();
});
elements.closeModalBtn.addEventListener('click', closeAllModals);
elements.closeUpdateBtn.addEventListener('click', closeAllModals);
elements.closeHistoryBtn.addEventListener('click', closeAllModals);
elements.modalBackdrop.addEventListener('click', closeAllModals);
// elements.addItemForm.addEventListener('submit', addItem); // REMOVED
elements.updatePriceForm.addEventListener('submit', updatePrice);
elements.addHistoryForm.addEventListener('submit', addHistoryEntry);
elements.navDashboard.addEventListener('click', () => { state.currentView = 'dashboard'; render(); });
elements.navActivity.addEventListener('click', () => { state.currentView = 'activity'; render(); });

function toggleModal(modal, show) {
    if (show) { modal.classList.remove('hidden'); elements.modalBackdrop.classList.remove('hidden'); }
    else { modal.classList.add('hidden'); elements.modalBackdrop.classList.add('hidden'); }
}

function closeAllModals() {
    elements.addItemModal.classList.add('hidden');
    elements.updatePriceModal.classList.add('hidden');
    elements.historyModal.classList.add('hidden');
    elements.modalBackdrop.classList.add('hidden');
    currentEditingItemId = null;

    // Reset form state
    elements.addItemForm.reset();
    elements.itemPriceInput.disabled = false;
    const submitBtn = elements.addItemForm.querySelector('button[type="submit"]');
    submitBtn.textContent = "Save Item";
    // Reset handler to default add
    elements.addItemForm.onsubmit = handleAddItemSubmit;
}

// Handler functions
async function handleAddItemSubmit(e) {
    e.preventDefault();
    const name = elements.itemNameInput.value;
    const priceVal = elements.itemPriceInput.value;
    const price = priceVal ? parseFloat(priceVal) : 0;
    const category = elements.itemCategoryInput.value;
    const excludeInput = document.getElementById('item-exclude');
    const exclude = excludeInput ? excludeInput.value : "";

    await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, category, price, excludeKeywords: exclude })
    });
    closeAllModals();
    await loadState();
}

async function handleEditItemSubmit(e) {
    e.preventDefault();
    if (!currentEditingItemId) return;

    const newName = elements.itemNameInput.value;
    const newCategory = elements.itemCategoryInput.value;
    const priceVal = elements.itemPriceInput.value;
    const newPrice = priceVal ? parseFloat(priceVal) : 0;

    const excludeInput = document.getElementById('item-exclude');
    const newExclude = excludeInput ? excludeInput.value : "";

    if (newName) {
        await fetch(`/api/items/${currentEditingItemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: newName,
                category: newCategory,
                price: newPrice, // Allow updating acquisition cost
                excludeKeywords: newExclude
            })
        });
        await loadState();
        closeAllModals();
    }
}

function openAddModal() {
    toggleModal(elements.addItemModal, true);
    elements.addItemForm.reset();
    elements.itemPriceInput.disabled = false;
    document.getElementById('modal-title').textContent = "Add New Item";
    const submitBtn = elements.addItemForm.querySelector('button[type="submit"]');
    submitBtn.textContent = "Save Item";

    elements.addItemForm.onsubmit = handleAddItemSubmit;
}

window.openEditModal = function (id) {
    const item = state.items.find(i => i.id === id);
    if (!item) return;

    currentEditingItemId = id;

    toggleModal(elements.addItemModal, true);
    document.getElementById('modal-title').textContent = "Edit Item Settings";

    elements.itemNameInput.value = item.name;
    elements.itemCategoryInput.value = item.category;
    elements.itemPriceInput.value = item.price;
    // Enable price editing as per user request
    elements.itemPriceInput.disabled = false;

    // Populate Exclude Keywords
    const excludeInput = document.getElementById('item-exclude');
    if (excludeInput) {
        excludeInput.value = item.excludeKeywords || "";
    }

    const submitBtn = elements.addItemForm.querySelector('button[type="submit"]');
    submitBtn.textContent = "Save Changes";

    // Set explicit edit handler
    elements.addItemForm.onsubmit = handleEditItemSubmit;
};

// --- Stats Toggle Logic (Added via Fix) ---
elements.toggleStatsBtn = document.getElementById('toggle-stats-btn');
elements.statsSection = document.getElementById('stats-section');
let statsVisible = true;

if (elements.toggleStatsBtn) {
    elements.toggleStatsBtn.addEventListener('click', () => {
        statsVisible = !statsVisible;
        if (statsVisible) {
            elements.statsSection.style.maxHeight = '500px';
            elements.statsSection.style.opacity = '1';
            elements.statsSection.style.marginBottom = '24px';
            elements.toggleStatsBtn.textContent = "Hide Stats ▲";
        } else {
            elements.statsSection.style.maxHeight = '0';
            elements.statsSection.style.opacity = '0';
            elements.statsSection.style.marginBottom = '0';
            elements.toggleStatsBtn.textContent = "Show Stats ▼";
        }
    });
}

// Init
loadState();

