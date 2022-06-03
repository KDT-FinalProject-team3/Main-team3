new Chart(document.getElementById("bar-chart-horizontal"), {
    type: 'horizontalBar',
    data: {
      labels: ["죽은", "자살한", "불면증", "자해", "나따위","한심한", "지옥", "하늘나라", "숨이", "겨우"],
      datasets: [
        {
          label: "위험 기준(언어적 신호)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850","#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [13,11,10,8,7,6,5,4,3,2,1]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: "사용된 단어 빈도 Top10(언어적 신호)"
      }
    }
});