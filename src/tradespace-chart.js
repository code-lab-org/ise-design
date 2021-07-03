require('chart.js/dist/chart.min.js');

export function createChart(displayDesign) {
  return new Chart("tradespace-chart", {
    // configure as scatter plot
    type: "scatter",
    // define datasets for valid and invalid designs
    data: {
      datasets: [
        {
          label: 'Valid',
          data: [],
          pointBackgroundColor: "#5cb85c",
          pointBorderColor: "#5cb85c",
          pointStyle: 'circle',
          pointRadius: 5
        }, {
          label: 'Invalid',
          data: [],
          pointBackgroundColor: "#d9534f",
          pointBorderColor: "#d9534f",
          pointBorderWidth: 3,
          pointStyle: 'crossRot',
          pointRadius: 5
        },
      ]
    },
    // configure chart options
    options: {
      // configure x and y axes
      scales: {
        x: {
          title: {
            text: "Cost",
            display: true
          },
          ticks: {
            callback: function(value, index, values) {
              return "$" + value.toFixed(2);
            }
          }
        },
        y: {
          title: {
            text: "Value",
            display: true
          },
          ticks: {
            callback: function(value, index, values) {
              return "$" + value.toFixed(2);
            }
          }
        }
      },
      // respond to clicks on points
      onClick: function(event, elements) {
        if(elements.length > 0) {
          // grab the design id of the first element
          var id = this.data.datasets[elements[0].datasetIndex].data[elements[0].index].raw.designId;
          // perform ajax request and display design
          $.ajax({
            method: "GET",
            url: 'designs/' + id,
            success: displayDesign
          });
        }
      },
      // configure chart plugins
      plugins: {
        // disable legend
        legend: {
          display: false
        },
        // add custom tooltips to show thumbnail images
        tooltip: {
          enabled: false,
          external: function(context) {
            // set curser to a pointer as clicking affordance
            $(this._chart.canvas).css('cursor', 'pointer');
            // get the tooltip element
            var tooltipEl = $('#chartjs-tooltip');
            // if it doensn't exist yet, create it
            if(tooltipEl.length === 0) {
              tooltipEl = $("<div id='chartjs-tooltip'></div>");
              $(this._chart.canvas.parentNode).append(tooltipEl);
            }
            // if tooltip should be hidden, hide it (and reset cursor to default)
            var tooltipModel = context.tooltip;
            if(tooltipModel.opacity === 0) {
              tooltipEl.css("opacity", 0);
              $(this._chart.canvas).css('cursor', 'default');
              return;
            }
            // reset tooltip classes
            tooltipEl.removeClass("above below no-transform");
            if(tooltipModel.yAlign) {
              tooltipEl.addClass(tooltipModel.yAlign);
            } else {
              tooltipEl.addClass("no-transform");
            }
            // add the tooltip content
            tooltipEl.html(
              tooltipModel.dataPoints.map(
                function(dataPoint) {
                  return "<div><img src='data:image/png;base64,"
                    + dataPoint.raw.raw.thumbnail
                    + "' width='100' /><div class='small font-weight-light text-center'>"
                    + dataPoint.raw.raw.name
                    + "</div></div>";
                }
              ).join("")
            );
            var position = context.chart.canvas.getBoundingClientRect();
            var bodyFont = Chart.helpers.toFont(tooltipModel.options.bodyFont);
            // set the tooltip style
            tooltipEl.css({
              "opacity": 1,
              "position": "absolute",
              "left": position.left + window.pageXOffset + tooltipModel.caretX + 'px',
              "top": position.top + window.pageYOffset + tooltipModel.caretY + 'px',
              "font": bodyFont.string,
              "padding": tooltipModel.padding + 'px ' + tooltipModel.padding + 'px',
              "pointerEvents": 'none'
            });
          }
        }
      }
    }
  });
};
