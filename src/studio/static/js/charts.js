(function() {
  /**
   * Resolve potential errors
   *
   * @param  {object} response Incoming response
   *
   * @return {object}          Same response
   */
  function resolveStatus(response) {
    if (!response.ok) {
      throw Error(response.statusText);
    }
    return response.json();
  }

  /**
   * Fetches chart's data
   *
   * @param  {string} metric      Type of the metric one of ('SESSIONS' or 'INTERACTIONS')
   * @param  {string} startDate   Starting date for chart presentation
   * @param  {string} endDate     Final date for chart presentation
   * @param  {string} color       Chart series color
   *
   */
  function fetchData(metric = 'SESSIONS', startDate, endDate, color) {
    fetch(`insights/chart/${ metric.toLowerCase() }`, { credentials: 'same-origin'})
      .then(resolveStatus)
      .then(response => drawChart(
        response, metric, new Date(startDate), new Date(endDate), color)
      )
      .catch(message => resolveError(message, metric));
  }

  /**
   * Triggers error messages
   *
   * @param  {string} message Error message
   * @param  {string} metric  Type of metric
   *
   */
  function resolveError(message, metric) {
    document.getElementById(metric).classList.add('error');
    console.error(message);
  }

  /**
   * Drws actual chart and remove loading class
   *
   * @param  {string} response    Error message
   * @param  {string} metric      Type of metric
   * @param  {string} startDate   Starting date for chart presentation
   * @param  {string} endDate     Final date for chart presentation
   * @param  {string} color       Chart series color
   *
   */
  function drawChart(response, metric, startDate, endDate, color) {
    if (response && response.objects) {
      const CONTAINER = document.getElementById(metric);
      const CANVAS = document.querySelector(`#${metric} .canvas`);
      const DATE_OPTION = {
        day: 'numeric',
        month: 'long',
        weekday: 'long',
        year: 'numeric'
      }

      var data = new google.visualization.DataTable();
      var chart = new google.visualization.ColumnChart(CANVAS);

      data.addColumn('datetime', 'Date');
      data.addColumn('number', metric);
      data.addRows(response.objects.length);

      response.objects.forEach((entry, index) => {
        data.setCell(index, 0, new Date(entry.date));
        data.setCell(index, 1, entry.count);
      })

      google.visualization.events.addListener(chart, 'ready', function readyHandler(event){
        CONTAINER.classList.remove('loading');
      });

      const OPTIONS = {
        backgroundColor: { fill: 'transparent' },
        bar: { groupWidth: '35' },
        colors: [ color ],
        hAxis: {
          baselineColor: '#808080',
          gridlines: { color: '#404040' },
          minValue: startDate,
          maxValue: endDate,
          textStyle: { color: '#999999' }
        },
        height: 300,
        legend: { position: 'none' },
        title: `Chat ${ metric.toLowerCase() } per day from ${ startDate.toLocaleString('en-US', DATE_OPTION) } to ${ endDate.toLocaleString('en-US', DATE_OPTION) }`,
        titleTextStyle: { color: 'white', fontSize: '16px' },
        vAxis: {
          format: 'short',
          gridlines: { color: '#404040' },
          textStyle: { color: '#999999' }
        },
        width: '90%'
      };

      chart.draw(data, OPTIONS);

    } else {
      throw Error('Error: no data');
    }
  }

  window.fetchData = fetchData;
})();
