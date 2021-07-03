require('datatables.net/js/jquery.dataTables.min.js');
require('datatables.net-bs4/css/dataTables.bootstrap4.min.css');
require('datatables.net-bs4/js/dataTables.bootstrap4.min.js');

var moment = require('moment');

export function createDataTable(user, chart) {
  return $("#tradespace-table").DataTable({
    // user server-side api
    serverSide: true,
    // ajax url for server-side api
    ajax: {
      url: "designs/",
      dataSrc: "designs"
    },
    // default order by column 1 (timestamp) in descending order
    order: [[ 1, 'desc' ]],
    // define columns
    columns: [
      {
        name: "id",
        data: {
          designId: "designId",
          thumbnail: "thumbnail"
        },
        searchable: true,
        orderable: false,
        render: function(data, type, row, meta) {
          return (
            "<a href='#' class='design-link' data-id='" + data.designId + "'>"
            + "<img src='data:image/png;base64," + data['thumbnail'] + "' width='100' /></a>"
            + (user.is_superuser ?
              "<button type='button' class='btn btn-sm btn-outline-danger delete-button m-2' data-id='"
              + data.designId + "'><i class='fa fa-trash-alt'></i></button>" : ""
            )
          );
        }
      }, {
        name: "timestamp",
        data: "timestamp",
        searchable: false,
        render: function(data, type, row, meta) {
          return moment.utc(data).local().format("M/D/YYYY h:mma");
        }
      }, {
        name: "designer",
        data: "designer",
        searchable: true,
      }, {
        name: "model",
        data: "name",
        searchable: true,
      }, {
        name: "valid",
        data: "isValid",
        searchable: false,
        render: function( data, type, row, meta) {
          return data ? "<i class='text-success fa fa-check-circle'></i>"
            : "<i class='text-danger fa fa-times-circle'></i>";
        }
      }, {
        name: "cost",
        data: "totalCost",
        searchable: false,
        render: function(data, type, row, meta) {
          return "$" + data.toFixed(2);
        }
      }, {
        name: "value",
        data: "totalRevenue",
        searchable: false,
        render: function(data, type, row, meta) {
          return "$" + data.toFixed(2);
        }
      }, {
        name: "profit",
        data: "totalProfit",
        searchable: false,
        render: function(data, type, row, meta) {
          return (
              "<span class='" + (data >= 0 ? "text-success" : "text-danger") + "'>"
              + (data < 0 ? "-" : "") + "$" + Math.abs(data).toFixed(2) + "</span>"
            );
        }
      }, {
        name: "roi",
        data: "totalRoi",
        searchable: false,
        render: function(data, type, row, meta) {
          return (
              "<span class='"+ (data >= 0 ? "text-success" : "text-danger") + "'>"
              + (100*data).toFixed(1) + "%</span>"
            );
        }
      }
    ],
    // update chart after drawing new table
    drawCallback: function(settings) {
      // remove any existing data from the chart dataset
      chart.data.datasets[0].data = [];
      chart.data.datasets[1].data = [];
      // extract the data from the table API
      var data = this.api().rows({"page": "current"}).data();
      // note that data is an object, rather than a list
      for(var i = 0; i < data.length; i++) {
        chart.data.datasets[data[i].isValid ? 0 : 1].data.push({
          x: data[i].cost.total,
          y: data[i].value.price,
          raw: data[i]
        });
      }
      // request chart to update display
      chart.update();
    }
  });
};
