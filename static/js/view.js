function filterLogs() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#logsTable tr');

    rows.forEach(row => {
        const title = row.getAttribute('data-title');
        row.style.display = title && title.includes(input) ? '' : 'none';
    });
}

async function removeLog(id) {
    const confirmed = confirm("Are you sure you want to delete this log?");
    if (!confirmed) return;

    const res = await fetch(`/delete-log/${id}`, { method: 'DELETE' });

    if (res.ok) {
        alert("Log removed!");
        location.reload();
    } else {
        alert("Failed to remove log.");
    }
}
