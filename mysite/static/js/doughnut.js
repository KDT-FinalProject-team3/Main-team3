new Chart(document.getElementById("doughnut-chart"), {
    type: 'doughnut',
    data: {
      labels: ["Death", "Afterlife", "Suicide_Method", "Self_Deprecation", "Suicide_Victim"],
      datasets: [
        {
          label: "위험 기준(언어적 신호)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [13,27,10,27,23]
        }
      ]
    },
    options: {
      title: {
        display: true,
        text: "위험 기준(언어적 신호)"
      }
    }
});