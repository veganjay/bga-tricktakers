let csvData = [];

function loadCSV(url) {
    fetch(url)
        .then(response => response.text())
        .then(text => {
            csvData = text.trim().split('\n').map(row => row.split(','));
            const headers = csvData.shift();
            const table = document.getElementById('csvTable');
            const tbody = document.createElement('tbody');

            // Create table headers
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                th.addEventListener('click', () => sortTable(header));
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);
            table.appendChild(tbody);

            populateTable(csvData);
        })
        .catch(error => console.error('Error loading CSV:', error));
}

function populateTable(data) {
    const tbody = document.getElementById('csvTable').querySelector('tbody');
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    data.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(cellData => {
            const td = document.createElement('td');
            td.textContent = cellData;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    filterTable();  // Apply initial filter
}

function sortTable(columnName) {
    const table = document.getElementById('csvTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${getIndex(columnName)})`).textContent.trim();
        const bValue = b.querySelector(`td:nth-child(${getIndex(columnName)})`).textContent.trim();
        return aValue.localeCompare(bValue);
    });

    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    rows.forEach(row => tbody.appendChild(row));
}

function getIndex(columnName) {
    const headers = Array.from(document.querySelectorAll('#csvTable th'));
    return headers.findIndex(th => th.textContent === columnName) + 1;
}

function filterTable() {
    const showBeta = document.getElementById('betaStatus').checked;
    const showAlpha = document.getElementById('alphaStatus').checked;

    const rows = document.querySelectorAll('#csvTable tbody tr');

    rows.forEach(row => {
        const status = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const matchesBeta = showBeta && status === 'beta';
        const matchesAlpha = showAlpha && status === 'alpha';
        const matchesPublic = status === 'public';

        if (matchesBeta || matchesAlpha || matchesPublic) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}
