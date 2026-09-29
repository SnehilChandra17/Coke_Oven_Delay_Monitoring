const API_URL = "http://127.0.0.1:8000";
let availableBatteries = [];

// =========================================================
// CHART INSTANCES
// =========================================================

let batteryChart = null;
let shiftChart = null;
let machineChart = null;
let agencyChart = null;

let delayTrendChart = null;
let attendedChart = null;
let mechanismChart = null;
let topMachineChart = null;


// =========================================================
// LOAD BATTERIES
// =========================================================

async function loadBatteries() {

    const batteryList =
        document.getElementById("batteryList");


    if (!batteryList) {

        console.error(
            "Battery list element #batteryList not found."
        );

        return;
    }


    try {

        // ---------------------------------------------
        // CALL BATTERY API
        // ---------------------------------------------

        const response =
            await fetch(
                `${API_URL}/api/batteries/`
            );


        if (!response.ok) {

            throw new Error(
                `Battery API failed with status ${response.status}`
            );
        }


        // ---------------------------------------------
        // READ RESPONSE
        // ---------------------------------------------

        const data =
            await response.json();


        console.log(
            "Battery API response:",
            data
        );


        // ---------------------------------------------
        // IMPORTANT:
        // Backend returns:
        //
        // {
        //     "data": [...]
        // }
        //
        // NOT:
        //
        // {
        //     "batteries": [...]
        // }
        // ---------------------------------------------

        const batteries =
            Array.isArray(data.data)
                ? data.data
                : [];


        // ---------------------------------------------
        // SAVE AVAILABLE BATTERIES
        // ---------------------------------------------

        availableBatteries =
            batteries.map(
                battery =>
                    String(
                        battery.battery_number
                    )
            );


        // ---------------------------------------------
        // CLEAR OLD OPTIONS
        // ---------------------------------------------

        batteryList.innerHTML = "";


        // ---------------------------------------------
        // ADD BATTERY OPTIONS
        // ---------------------------------------------

        batteries.forEach(
            function (battery) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    battery.battery_number;


                batteryList.appendChild(
                    option
                );
            }
        );


        console.log(
            "Available batteries:",
            availableBatteries
        );


    } catch (error) {

        console.error(
            "Battery loading error:",
            error
        );


        showError(
            "Unable to load battery list. " +
            "Make sure the FastAPI server is running."
        );
    }
}

// =========================================================
// LOAD DASHBOARD
// =========================================================

async function loadDashboard() {

    try {

        await loadSummary();

        await loadBatteryChart();

        await loadShiftChart();

        await loadMachineChart();

        await loadAgencyChart();

        await loadAdvancedCharts();

    }

    catch (error) {

        console.error(error);

        showError(
            "Unable to load dashboard data."
        );
    }
}

// =========================================================
// LOAD ADVANCED CHARTS
// =========================================================

async function loadAdvancedCharts() {

    try {

        const response = await fetch(
            `${API_URL}/api/analytics/filtered?start_date=2018-04-20&end_date=2018-04-26`
        );

        if (!response.ok) {
            throw new Error(
                "Advanced analytics API failed"
            );
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }


        // Existing dashboard charts

        updateBatteryChart(
            data.by_battery
        );

        updateShiftChart(
            data.by_shift
        );

        updateMachineChart(
            data.by_machine
        );

        updateAgencyChart(
            data.by_agency
        );


        // New advanced charts

        updateDelayTrendChart(
            data.by_date
        );

        updateAttendedChart(
            data.by_attended
        );

        updateMechanismChart(
            data.by_mechanism
        );

        updateTopMachineChart(
            data.by_machine
        );

    } catch (error) {

        console.error(
            "Advanced charts error:",
            error
        );

        throw error;
    }
}


// =========================================================
// SUMMARY
// =========================================================

async function loadSummary() {

    const response = await fetch(
        `${API_URL}/api/analytics/summary`
    );

    if (!response.ok) {

        throw new Error(
            "Summary API failed"
        );

    }

    const data =
        await response.json();


    document.getElementById(
        "dashboardRecords"
    ).textContent =
        data.total_records;


    document.getElementById(
        "dashboardDelay"
    ).textContent =
        `${data.total_delay_minutes} min`;


    document.getElementById(
        "dashboardHours"
    ).textContent =
        `${data.total_delay_hours} hrs`;


    document.getElementById(
        "dashboardAverage"
    ).textContent =
        `${data.average_delay_minutes} min`;
}


// =========================================================
// BATTERY CHART
// =========================================================

async function loadBatteryChart() {

    const response = await fetch(
        `${API_URL}/api/analytics/battery`
    );

    const data =
        await response.json();


    const labels =
        data.data.map(
            item => `Battery ${item.battery}`
        );


    const values =
        data.data.map(
            item => item.total_delay_minutes
        );


    if (batteryChart) {

        batteryChart.destroy();

    }


    const ctx =
        document.getElementById(
            "batteryChart"
        );


    batteryChart = new Chart(
        ctx,
        {
            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label:
                            "Delay (minutes)",

                        data: values
                    }
                ]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true

                    }

                }

            }
        }
    );
}


// =========================================================
// SHIFT CHART
// =========================================================

async function loadShiftChart() {

    const response = await fetch(
        `${API_URL}/api/analytics/shift`
    );

    const data =
        await response.json();


    const labels =
        data.data.map(
            item => `Shift ${item.shift}`
        );


    const values =
        data.data.map(
            item => item.total_delay_minutes
        );


    if (shiftChart) {

        shiftChart.destroy();

    }


    const ctx =
        document.getElementById(
            "shiftChart"
        );


    shiftChart = new Chart(
        ctx,
        {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [
                    {
                        label:
                            "Delay (minutes)",

                        data: values
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false

            }

        }
    );
}


// =========================================================
// MACHINE CHART
// =========================================================

async function loadMachineChart() {

    const response = await fetch(
        `${API_URL}/api/analytics/machine`
    );

    const data =
        await response.json();


    const labels =
        data.data.map(
            item => item.machine
        );


    const values =
        data.data.map(
            item => item.total_delay_minutes
        );


    if (machineChart) {

        machineChart.destroy();

    }


    const ctx =
        document.getElementById(
            "machineChart"
        );


    machineChart = new Chart(
        ctx,
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label:
                            "Delay (minutes)",

                        data: values
                    }
                ]

            },

            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {

                        beginAtZero: true

                    }

                }

            }

        }
    );
}


// =========================================================
// AGENCY CHART
// =========================================================

async function loadAgencyChart() {

    const response = await fetch(
        `${API_URL}/api/analytics/agency`
    );

    const data =
        await response.json();


    const labels =
        data.data.map(
            item => item.agency
        );


    const values =
        data.data.map(
            item => item.total_delay_minutes
        );


    if (agencyChart) {

        agencyChart.destroy();

    }


    const ctx =
        document.getElementById(
            "agencyChart"
        );


    agencyChart = new Chart(
        ctx,
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label:
                            "Delay (minutes)",

                        data: values
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true

                    }

                }

            }

        }
    );
}

// =========================================================
// ADVANCED CHARTS
// =========================================================

// =========================================================
// DELAY TREND CHART — IMPROVED
// =========================================================

function updateDelayTrendChart(data) {

    // ---------------------------------------------------------
    // Safety check
    // ---------------------------------------------------------

    if (!Array.isArray(data)) {
        console.warn(
            "Delay trend data is not available."
        );
        return;
    }


    // ---------------------------------------------------------
    // Prepare chart data
    // ---------------------------------------------------------

    const labels = data.map(function (item) {

        if (!item.date) {
            return "Unknown";
        }

        // Convert YYYY-MM-DD to DD Mon YYYY
        const date = new Date(
            item.date + "T00:00:00"
        );

        if (isNaN(date.getTime())) {
            return item.date;
        }

        return date.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );
    });


    const values = data.map(function (item) {

        return Number(
            item.total_delay_minutes || 0
        );

    });


    // ---------------------------------------------------------
    // Destroy previous chart
    // ---------------------------------------------------------

    if (delayTrendChart) {

        delayTrendChart.destroy();

        delayTrendChart = null;
    }


    // ---------------------------------------------------------
    // Get canvas
    // ---------------------------------------------------------

    const ctx =
        document.getElementById(
            "delayTrendChart"
        );


    if (!ctx) {

        console.warn(
            "delayTrendChart canvas not found."
        );

        return;
    }


    // ---------------------------------------------------------
    // Create chart
    // ---------------------------------------------------------

    delayTrendChart = new Chart(
        ctx,
        {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {

                        label:
                            "Delay (minutes)",

                        data:
                            values,

                        fill: true,

                        tension: 0.35,

                        pointRadius: 5,

                        pointHoverRadius: 7,

                        borderWidth: 2

                    }

                ]

            },


            options: {

                responsive: true,

                maintainAspectRatio: false,


                interaction: {

                    mode: "index",

                    intersect: false

                },


                plugins: {

                    legend: {

                        display: true,

                        position: "top"

                    },


                    tooltip: {

                        callbacks: {

                            title: function (
                                tooltipItems
                            ) {

                                return tooltipItems[0]
                                    .label;
                            },


                            label: function (
                                context
                            ) {

                                const minutes =
                                    Number(
                                        context.parsed.y || 0
                                    );

                                const hours =
                                    minutes / 60;


                                return [
                                    `Delay: ${minutes} minutes`,
                                    `Hours: ${hours.toFixed(2)} hrs`
                                ];

                            }

                        }

                    }

                },


                scales: {

                    x: {

                        title: {

                            display: true,

                            text:
                                "Date"

                        },

                        ticks: {

                            autoSkip: false,

                            maxRotation: 45,

                            minRotation: 0

                        }

                    },


                    y: {

                        beginAtZero: true,

                        title: {

                            display: true,

                            text:
                                "Delay (minutes)"

                        },

                        ticks: {

                            callback:
                                function (value) {

                                    return value +
                                        " min";

                                }

                        }

                    }

                }

            }

        }
    );
}
// =========================================================
// ATTENDED VS UNATTENDED CHART
// =========================================================

function updateAttendedChart(data) {

    const labels = data.map(
        item => item.attended || "Unknown"
    );

    const values = data.map(
        item => item.total_delay_minutes
    );

    if (attendedChart) {

        attendedChart.destroy();

    }

    const ctx = document.getElementById(
        "attendedChart"
    );

    attendedChart = new Chart(
        ctx,
        {
            type: "doughnut",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Delay (minutes)",

                        data: values
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom"

                    },

                    tooltip: {

                        callbacks: {

                            label: function(context) {

                                const item =
                                    data[context.dataIndex];

                                return `${context.label}: ${item.total_delay_minutes} min (${item.record_count} records)`;

                            }

                        }

                    }

                }

            }

        }
    );
}


// =========================================================
// TOP DELAY MECHANISMS — IMPROVED
// =========================================================

function updateMechanismChart(data) {

    // ---------------------------------------------------------
    // Safety check
    // ---------------------------------------------------------

    if (!Array.isArray(data)) {

        console.warn(
            "Mechanism data is not available."
        );

        return;
    }


    // ---------------------------------------------------------
    // Remove invalid records
    // ---------------------------------------------------------

    const validData = data.filter(function (item) {

        return item &&
            item.mechanism &&
            Number(item.total_delay_minutes || 0) >= 0;

    });


    // ---------------------------------------------------------
    // Sort by highest delay
    // ---------------------------------------------------------

    validData.sort(function (a, b) {

        return Number(
            b.total_delay_minutes || 0
        ) - Number(
            a.total_delay_minutes || 0
        );

    });


    // ---------------------------------------------------------
    // Take top 10 mechanisms
    // ---------------------------------------------------------

    const topMechanisms =
        validData.slice(0, 10);


    // ---------------------------------------------------------
    // Prepare chart data
    // ---------------------------------------------------------

    const labels =
        topMechanisms.map(function (item) {

            return item.mechanism;

        });


    const values =
        topMechanisms.map(function (item) {

            return Number(
                item.total_delay_minutes || 0
            );

        });


    // ---------------------------------------------------------
    // Destroy previous chart
    // ---------------------------------------------------------

    if (mechanismChart) {

        mechanismChart.destroy();

        mechanismChart = null;

    }


    // ---------------------------------------------------------
    // Get canvas
    // ---------------------------------------------------------

    const canvas =
        document.getElementById(
            "mechanismChart"
        );


    if (!canvas) {

        console.warn(
            "mechanismChart canvas not found."
        );

        return;

    }


    // ---------------------------------------------------------
    // Empty data handling
    // ---------------------------------------------------------

    if (topMechanisms.length === 0) {

        const ctx =
            canvas.getContext("2d");

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        return;

    }


    // ---------------------------------------------------------
    // Create chart
    // ---------------------------------------------------------

    mechanismChart = new Chart(

        canvas,

        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [

                    {

                        label:
                            "Total Delay (minutes)",

                        data: values,

                        borderWidth: 1

                    }

                ]

            },


            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,


                interaction: {

                    mode: "index",

                    intersect: false

                },


                plugins: {

                    legend: {

                        display: false

                    },


                    tooltip: {

                        callbacks: {

                            title: function (
                                tooltipItems
                            ) {

                                return tooltipItems[0]
                                    .label;

                            },


                            label: function (
                                context
                            ) {

                                const minutes =
                                    Number(
                                        context.parsed.x || 0
                                    );

                                const hours =
                                    minutes / 60;


                                return [
                                    `Delay: ${minutes} minutes`,
                                    `Hours: ${hours.toFixed(2)} hrs`
                                ];

                            }

                        }

                    }

                },


                scales: {

                    x: {

                        beginAtZero: true,

                        title: {

                            display: true,

                            text:
                                "Total Delay (minutes)"

                        },


                        ticks: {

                            callback:
                                function (value) {

                                    return value +
                                        " min";

                                }

                        }

                    },


                    y: {

                        title: {

                            display: true,

                            text:
                                "Mechanism"

                        }

                    }

                }

            }

        }

    );

}

// =========================================================
// TOP DELAY MACHINES
// =========================================================

function updateTopMachineChart(data) {

    const topData = data.slice(0, 10);

    const labels = topData.map(
        item => item.machine
    );

    const values = topData.map(
        item => item.total_delay_minutes
    );

    if (topMachineChart) {

        topMachineChart.destroy();

    }

    const ctx = document.getElementById(
        "topMachineChart"
    );

    topMachineChart = new Chart(
        ctx,
        {
            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Delay (minutes)",

                        data: values
                    }
                ]

            },

            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        display: false

                    },

                    tooltip: {

                        callbacks: {

                            label: function(context) {

                                return `${context.parsed.x} minutes`;

                            }

                        }

                    }

                },

                scales: {

                    x: {

                        beginAtZero: true,

                        title: {

                            display: true,

                            text: "Delay (minutes)"

                        }

                    }

                }

            }

        }
    );
}

// =========================================================
// SEARCH DELAYS
// =========================================================

async function searchDelays() {

    const battery =
        document.getElementById("battery").value.trim();

    const date =
        document.getElementById("date").value;

    const time =
        document.getElementById("time").value;

    clearResults();

    // -----------------------------
    // VALIDATION
    // -----------------------------

    if (!battery) {
        showError("Please select a battery.");
        return;
    }

    if (!date) {
        showError("Please select a date.");
        return;
    }

    hideError();
    showLoading();

    const button =
        document.getElementById("searchButton");

    button.disabled = true;

    try {

        // -----------------------------
        // BUILD API URL
        // -----------------------------

        let url =
            `${API_URL}/api/delays/?` +
            `battery=${encodeURIComponent(battery)}` +
            `&date=${encodeURIComponent(date)}`;

        if (time) {
            url +=
                `&time=${encodeURIComponent(time)}`;
        }

        console.log("Searching:", url);

        // -----------------------------
        // CALL BACKEND
        // -----------------------------

        const response =
            await fetch(url);

        // -----------------------------
        // HANDLE ERROR
        // -----------------------------

        if (!response.ok) {

            let errorMessage =
                "Failed to fetch delay records.";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.detail ||
                    errorMessage;

            } catch (e) {
                // Server did not return JSON
            }

            throw new Error(errorMessage);
        }

        // -----------------------------
        // GET JSON RESPONSE
        // -----------------------------

        const data =
            await response.json();

        console.log("API Response:", data);

        // -----------------------------
        // DISPLAY RESULTS
        // -----------------------------

        displayResults(data);

    }

    catch (error) {

        console.error(
            "Search error:",
            error
        );

        showError(
            error.message ||
            "Something went wrong while searching."
        );

    }

    finally {

        hideLoading();

        button.disabled = false;
    }
}

// =========================================================
// DISPLAY SEARCH RESULTS
// =========================================================

function displayResults(data) {

    const summarySection =
        document.getElementById(
            "summarySection"
        );


    const resultsSection =
        document.getElementById(
            "resultsSection"
        );


    const resultsBody =
        document.getElementById(
            "resultsBody"
        );


    document.getElementById(
        "totalRecords"
    ).textContent =
        data.total_records;


    document.getElementById(
        "totalDelay"
    ).textContent =
        `${data.total_delay_minutes} min`;


    document.getElementById(
        "totalHours"
    ).textContent =
        `${data.total_delay_hours} hrs`;


    document.getElementById(
        "selectedBattery"
    ).textContent =
        `Battery ${data.battery}`;


    let searchText =
        `Battery ${data.battery} | ${data.date}`;


    if (data.time) {

        searchText +=
            ` | Time ${data.time}`;

    }


    document.getElementById(
        "searchInfo"
    ).textContent =
        searchText;


    resultsBody.innerHTML = "";


    if (data.records.length === 0) {

        resultsBody.innerHTML = `

            <tr>

                <td
                    colspan="11"
                    style="text-align:center;"
                >

                    No delay records found.

                </td>

            </tr>

        `;

    }


    data.records.forEach(
        function (record) {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>${record.date}</td>

                <td>${record.shift}</td>

                <td>${record.battery}</td>

                <td>${record.machine}</td>

                <td>${record.mechanism}</td>

                <td>${record.agency}</td>

                <td>${record.start_time}</td>

                <td>${record.end_time}</td>

                <td>
                    ${record.delay_minutes} min
                </td>

                <td>
                    ${record.attended || "-"}
                </td>

                <td>
                    ${record.remark || "-"}
                </td>

            `;


            resultsBody.appendChild(row);

        }
    );


    summarySection.classList.remove(
        "hidden"
    );


    resultsSection.classList.remove(
        "hidden"
    );
}

// =========================================================
// CLEAR SEARCH RESULTS
// =========================================================

function clearResults() {

    const summarySection =
        document.getElementById(
            "summarySection"
        );

    const resultsSection =
        document.getElementById(
            "resultsSection"
        );

    const resultsBody =
        document.getElementById(
            "resultsBody"
        );


    summarySection.classList.add(
        "hidden"
    );

    resultsSection.classList.add(
        "hidden"
    );

    resultsBody.innerHTML = "";

}
// =========================================================
//  VIEW BATTERY HISTORY
// =========================================================
async function viewBatteryHistory() {

    const battery =
        document.getElementById(
            "battery"
        ).value.trim();


    clearResults();


    if (!battery) {

        showError(
            "Please select a battery first."
        );

        return;
    }


    if (!availableBatteries.includes(battery)) {

        showError(
            `Battery ${battery} is not available. ` +
            `Please select a valid battery.`
        );

        return;
    }


    hideError();

    showLoading();


    try {

        const response =
            await fetch(
                `${API_URL}/api/batteries/${battery}/history`
            );


        if (!response.ok) {

            const errorData =
                await response.json();

            throw new Error(
                errorData.detail ||
                "Failed to fetch battery history."
            );

        }


        const data =
            await response.json();


        displayHistory(data);

    }

    catch (error) {

        console.error(error);

        showError(
            error.message
        );

    }

    finally {

        hideLoading();

    }
}

// =========================================================
// DISPLAY BATTERY HISTORY
// =========================================================

function displayHistory(data) {

    const summarySection =
        document.getElementById(
            "summarySection"
        );


    const resultsSection =
        document.getElementById(
            "resultsSection"
        );


    const resultsBody =
        document.getElementById(
            "resultsBody"
        );


    // Summary

    document.getElementById(
        "totalRecords"
    ).textContent =
        data.total_records;


    document.getElementById(
        "totalDelay"
    ).textContent =
        `${data.total_delay_minutes} min`;


    document.getElementById(
        "totalHours"
    ).textContent =
        `${data.total_delay_hours} hrs`;


    document.getElementById(
        "selectedBattery"
    ).textContent =
        `Battery ${data.battery}`;


    // Information

    document.getElementById(
        "searchInfo"
    ).textContent =
        `Complete history for Battery ${data.battery}`;


    // Clear previous records

    resultsBody.innerHTML = "";


    // No records

    if (data.records.length === 0) {

        resultsBody.innerHTML = `

            <tr>

                <td
                    colspan="11"
                    style="text-align:center;"
                >

                    No delay history found.

                </td>

            </tr>

        `;

    }


    // Display records

    data.records.forEach(
        function (record) {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>${record.date}</td>

                <td>${record.shift}</td>

                <td>${record.battery}</td>

                <td>${record.machine}</td>

                <td>${record.mechanism}</td>

                <td>${record.agency}</td>

                <td>${record.start_time}</td>

                <td>${record.end_time}</td>

                <td>
                    ${record.delay_minutes} min
                </td>

                <td>
                    ${record.attended || "-"}
                </td>

                <td>
                    ${record.remark || "-"}
                </td>

            `;


            resultsBody.appendChild(row);

        }
    );


    summarySection.classList.remove(
        "hidden"
    );


    resultsSection.classList.remove(
        "hidden"
    );
}


// =========================================================
// ERROR HANDLING
// =========================================================

function showError(message) {

    const errorElement =
        document.getElementById(
            "errorMessage"
        );


    errorElement.textContent =
        message;


    errorElement.classList.remove(
        "hidden"
    );
}


function hideError() {

    document.getElementById(
        "errorMessage"
    ).classList.add(
        "hidden"
    );
}


// =========================================================
// LOADING
// =========================================================

function showLoading() {

    document.getElementById(
        "loading"
    ).classList.remove(
        "hidden"
    );
}


function hideLoading() {

    document.getElementById(
        "loading"
    ).classList.add(
        "hidden"
    );
}

// =========================================================
// DATE-RANGE ANALYTICS
// =========================================================

async function applyAnalyticsFilter() {

    const startDate =
        document.getElementById(
            "analyticsStartDate"
        ).value;

    const endDate =
        document.getElementById(
            "analyticsEndDate"
        ).value;

    const battery =
        document.getElementById(
            "analyticsBattery"
        ).value;

    const machine =
        document.getElementById(
            "analyticsMachine"
        ).value;

    const agency =
        document.getElementById(
            "analyticsAgency"
        ).value;

    const shift =
        document.getElementById(
            "analyticsShift"
        ).value;


    if (!startDate || !endDate) {

        showError(
            "Please select both start date and end date."
        );

        return;
    }


    if (startDate > endDate) {

        showError(
            "Start date cannot be later than end date."
        );

        return;
    }


    hideError();
    showLoading();


    const button =
        document.getElementById(
            "applyAnalyticsButton"
        );

    button.disabled = true;


    try {

        const params =
            new URLSearchParams();


        params.append(
            "start_date",
            startDate
        );


        params.append(
            "end_date",
            endDate
        );


        if (battery) {

            params.append(
                "battery",
                battery
            );

        }


        if (machine) {

            params.append(
                "machine",
                machine
            );

        }


        if (agency) {

            params.append(
                "agency",
                agency
            );

        }


        if (shift) {

            params.append(
                "shift",
                shift
            );

        }


        const response =
            await fetch(
                `${API_URL}/api/analytics/filtered?${params.toString()}`
            );


        if (!response.ok) {

            const errorData =
                await response.json();

            throw new Error(
                errorData.detail ||
                "Failed to load filtered analytics."
            );

        }


        const data =
            await response.json();


        if (data.error) {

            throw new Error(
                data.error
            );

        }


        displayFilteredAnalytics(data);

    }

    catch (error) {

        console.error(error);

        showError(
            error.message
        );

    }

    finally {

        hideLoading();

        button.disabled = false;

    }
}


// =========================================================
// DISPLAY FILTERED ANALYTICS
// =========================================================
function displayFilteredAnalytics(data) {

    const summary = data.summary;


    // =====================================================
    // UPDATE KPI CARDS
    // =====================================================

    document.getElementById(
        "dashboardRecords"
    ).textContent =
        summary.total_records;


    document.getElementById(
        "dashboardDelay"
    ).textContent =
        `${summary.total_delay_minutes} min`;


    document.getElementById(
        "dashboardHours"
    ).textContent =
        `${summary.total_delay_hours} hrs`;


    document.getElementById(
        "dashboardAverage"
    ).textContent =
        `${summary.average_delay_minutes} min`;


    // =====================================================
    // EXISTING CHARTS
    // =====================================================

    updateBatteryChart(
        data.by_battery
    );

    updateShiftChart(
        data.by_shift
    );

    updateMachineChart(
        data.by_machine
    );

    updateAgencyChart(
        data.by_agency
    );


    // =====================================================
    // NEW ADVANCED CHARTS
    // =====================================================

    updateDelayTrendChart(
        data.by_date
    );

    updateAttendedChart(
        data.by_attended
    );

    updateMechanismChart(
        data.by_mechanism
    );

    updateTopMachineChart(
        data.by_machine
    );
}



// =========================================================
// UPDATE BATTERY CHART
// =========================================================

function updateBatteryChart(data) {

    const labels =
        data.map(
            item => `Battery ${item.battery}`
        );


    const values =
        data.map(
            item => item.total_delay_minutes
        );


    if (batteryChart) {

        batteryChart.destroy();

    }


    const ctx =
        document.getElementById(
            "batteryChart"
        );


    batteryChart = new Chart(
        ctx,
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Delay (minutes)",
                        data: values
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {
                        beginAtZero: true
                    }

                }

            }

        }
    );
}


// =========================================================
// UPDATE SHIFT CHART
// =========================================================

function updateShiftChart(data) {

    const labels =
        data.map(
            item => `Shift ${item.shift}`
        );


    const values =
        data.map(
            item => item.total_delay_minutes
        );


    if (shiftChart) {

        shiftChart.destroy();

    }


    const ctx =
        document.getElementById(
            "shiftChart"
        );


    shiftChart = new Chart(
        ctx,
        {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Delay (minutes)",
                        data: values
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false

            }

        }
    );
}


// =========================================================
// UPDATE MACHINE CHART
// =========================================================

function updateMachineChart(data) {

    const labels =
        data.map(
            item => item.machine
        );


    const values =
        data.map(
            item => item.total_delay_minutes
        );


    if (machineChart) {

        machineChart.destroy();

    }


    const ctx =
        document.getElementById(
            "machineChart"
        );


    machineChart = new Chart(
        ctx,
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Delay (minutes)",
                        data: values
                    }
                ]

            },

            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {
                        beginAtZero: true
                    }

                }

            }

        }
    );
}


// =========================================================
// UPDATE AGENCY CHART
// =========================================================

function updateAgencyChart(data) {

    const labels =
        data.map(
            item => item.agency
        );


    const values =
        data.map(
            item => item.total_delay_minutes
        );


    if (agencyChart) {

        agencyChart.destroy();

    }


    const ctx =
        document.getElementById(
            "agencyChart"
        );


    agencyChart = new Chart(
        ctx,
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Delay (minutes)",
                        data: values
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {
                        beginAtZero: true
                    }

                }

            }

        }
    );
}


// =========================================================
// RESET ANALYTICS FILTER
// =========================================================

function resetAnalyticsFilter() {

    document.getElementById(
        "analyticsStartDate"
    ).value = "2018-04-20";


    document.getElementById(
        "analyticsEndDate"
    ).value = "2018-04-26";


    document.getElementById(
        "analyticsBattery"
    ).value = "";


    document.getElementById(
        "analyticsMachine"
    ).value = "";


    document.getElementById(
        "analyticsAgency"
    ).value = "";


    document.getElementById(
        "analyticsShift"
    ).value = "";


    hideError();


    loadDashboard();
}

// =========================================================
// LOAD ANALYTICS FILTER OPTIONS
// =========================================================

async function loadAnalyticsFilterOptions() {

    try {

        const response =
            await fetch(
                `${API_URL}/api/analytics/filtered?` +
                `start_date=2018-04-20&` +
                `end_date=2018-04-26`
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load analytics filter options."
            );

        }


        const data =
            await response.json();


        // -----------------------------------------
        // BATTERIES
        // -----------------------------------------

        const batterySelect =
            document.getElementById(
                "analyticsBattery"
            );


        data.by_battery.forEach(
            function (item) {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    item.battery;

                option.textContent =
                    `Battery ${item.battery}`;

                batterySelect.appendChild(
                    option
                );

            }
        );


        // -----------------------------------------
        // MACHINES
        // -----------------------------------------

        const machineSelect =
            document.getElementById(
                "analyticsMachine"
            );


        data.by_machine.forEach(
            function (item) {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    item.machine;

                option.textContent =
                    item.machine;

                machineSelect.appendChild(
                    option
                );

            }
        );


        // -----------------------------------------
        // AGENCIES
        // -----------------------------------------

        const agencySelect =
            document.getElementById(
                "analyticsAgency"
            );


        data.by_agency.forEach(
            function (item) {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    item.agency;

                option.textContent =
                    item.agency;

                agencySelect.appendChild(
                    option
                );

            }
        );

    }

    catch (error) {

        console.error(error);

        showError(
            "Unable to load analytics filter options."
        );

    }
}


// =========================================================
// INITIALIZE
// =========================================================
document.addEventListener(
    "DOMContentLoaded",
    async function () {

        await loadBatteries();

        await loadAnalyticsFilterOptions();

        await loadDashboard();

    }
);