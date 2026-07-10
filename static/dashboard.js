
// --------------------
// Risk Pie Chart
// --------------------
const riskCanvas = document.getElementById("riskChart");

if (riskCanvas) {

    const riskChart = new Chart(riskCanvas.getContext("2d"), {

        type: "pie",

        data: {

            labels: ["Safe", "Suspicious", "High Risk"],

            datasets: [{

                data: [
                    safeCount,
                    suspiciousCount,
                    highRiskCount
                ],

                backgroundColor: [
                    "#22c55e",
                    "#facc15",
                    "#ef4444"
                ],

                borderColor: "#ffffff",
                borderWidth: 2

            }]

        },

        options: {

            responsive: true,

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        color: "white"

                    }

                }

            }

        }

    });

}



// --------------------
// Friend Chart
// --------------------

const friendCanvas = document.getElementById("friendChart");

if (friendCanvas) {

    const friendChart = new Chart(friendCanvas.getContext("2d"), {

        type: "bar",

        data: {

            labels: [
                "Safe",
                "Caution",
                "Avoid"
            ],

            datasets: [{

                label: "Friend Requests",

                data: [
                    safeFriend,
                    cautionFriend,
                    avoidFriend
                ],

                backgroundColor: [
                    "#22c55e",
                    "#facc15",
                    "#ef4444"
                ]

            }]

        },

        options: {

            responsive: true,

            scales: {

                y: {

                    beginAtZero: true,

                    ticks: {

                        color: "white"

                    }

                },

                x: {

                    ticks: {

                        color: "white"

                    }

                }

            },

            plugins: {

                legend: {

                    labels: {

                        color: "white"

                    }

                }

            }

        }

    });

}