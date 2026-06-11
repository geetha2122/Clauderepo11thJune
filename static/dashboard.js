import { format, formatDistanceToNow } from 'https://cdn.jsdelivr.net/npm/date-fns@3.0.0/+esm';

const app = document.getElementById('root');

async function loadSessions(date) {
    const dateStr = format(date, 'yyyy-MM-dd');
    const response = await fetch(`/api/sessions?date=${dateStr}`);
    return response.json();
}

function formatDateWithOrdinal(date) {
    const formatter = new Intl.DateTimeFormat('en-US', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    const parts = formatter.formatToParts(date);

    const day = parseInt(parts.find(p => p.type === 'day').value);
    const month = parts.find(p => p.type === 'month').value;
    const year = parts.find(p => p.type === 'year').value;

    const ordinal = getOrdinalSuffix(day);
    return `${day}${ordinal} ${month} ${year}`;
}

function getOrdinalSuffix(day) {
    if (day > 3 && day < 21) return 'th';
    switch (day % 10) {
        case 1: return 'st';
        case 2: return 'nd';
        case 3: return 'rd';
        default: return 'th';
    }
}

function renderSession(session) {
    const typeColors = {
        'event': 'bg-blue-100 text-blue-800',
        'task': 'bg-yellow-100 text-yellow-800',
        'reminder': 'bg-red-100 text-red-800'
    };

    return `
        <div class="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <h3 class="font-semibold text-gray-900">${session.title}</h3>
                    <span class="inline-block mt-1 px-2 py-1 text-xs font-medium rounded ${typeColors[session.type] || 'bg-gray-100'}">
                        ${session.type}
                    </span>
                </div>
            </div>
            ${session.start_time ? `<p class="mt-2 text-sm text-gray-600">${session.start_time} - ${session.end_time || 'TBD'}</p>` : ''}
            ${session.description ? `<p class="mt-2 text-sm text-gray-700">${session.description}</p>` : ''}
        </div>
    `;
}

async function renderDashboard(date = new Date()) {
    const sessions = await loadSessions(date);

    app.innerHTML = `
        <div class="max-w-4xl mx-auto p-6">
            <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
                <h1 class="text-3xl font-bold text-gray-900 mb-4">Calendar Dashboard</h1>

                <div class="flex items-center gap-4 mb-6">
                    <input type="date" id="datePicker" value="${format(date, 'yyyy-MM-dd')}"
                           class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button id="todayBtn" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        Today
                    </button>
                </div>

                <h2 class="text-xl font-semibold text-gray-800 mb-4">${formatDateWithOrdinal(date)}</h2>

                <div class="grid gap-4">
                    ${sessions.length > 0 ? sessions.map(renderSession).join('') : '<p class="text-gray-500 py-8 text-center">No events, tasks or reminders scheduled for this date</p>'}
                </div>
            </div>
        </div>
    `;

    document.getElementById('datePicker').addEventListener('change', (e) => {
        renderDashboard(new Date(e.target.value));
    });

    document.getElementById('todayBtn').addEventListener('click', () => {
        renderDashboard(new Date());
    });
}

renderDashboard();
