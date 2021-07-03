require('bootstrap/dist/js/bootstrap.min.js');
require('bootstrap/dist/css/bootstrap.min.css');

require('@fortawesome/fontawesome-free/css/fontawesome.min.css');
require('@fortawesome/fontawesome-free/css/solid.min.css');

require('chart.js/dist/chart.min.js');

require('./style.css');

import paletteXML from '../resources/ISE_Palette.xml';
import modelaIO from '../resources/ModelA.io';
import './images/model-a-render.png';
import './images/model-a-bricklink.png';
import './favicon.ico';

import { createDataTable } from "./tradespace-table.js"
import { createChart } from "./tradespace-chart.js"

// helper function to format requirements analysis labels
function updateRequirementsAnalysisLabel(id, isValid, message) {
  if(isValid) {
    $(id).removeClass("text-secondary fa-times-circle text-danger");
    $(id).addClass("fa-check-circle text-success");
    $(id+"-message").addClass("text-success");
    $(id+"-message").removeClass("text-danger text-secondary");
    $(id+"-message").html(message);
  } else {
    $(id).removeClass("text-secondary fa-check-circle text-success");
    $(id).addClass("fa-times-circle text-danger");
    $(id+"-message").addClass("text-danger");
    $(id+"-message").removeClass("text-success text-secondary");
    $(id+"-message").html(message);
  }
};

// helper function to format requirements analysis descriptions
function getRequirementsAnalysisDescription(requirement, minCount) {
  return requirement.value ? 'Valid' : (
    requirement.count + " detected."
    + (
      requirement.count < minCount
        || !requirement.alignment
        || requirement.alignment.reduce(
          function(total, value) {
            return total && value;
          },
          true
        ) ? "" : requirement.alignment.map(
          function(value, index) {
            return value ? "" : (" #" + (index + 1));
          }
        ).join(",") + " not aligned correctly."
    ) + (
      requirement.count < minCount
        || !requirement.positioning
        || requirement.positioning.reduce(
          function(total, value) { return total && value; }, true
        ) ? "" :
        requirement.positioning.map(
          function(value, index) {
            return value ? "" : (" #" + (index + 1));
          }
        ).join(",") + " not positioned correctly."
    )
  );
};

// helper function to format market analysis labels
function updateMarketAnalysisLabel(id, value) {
  $(id).text(value.toFixed(0));
  if(value >= 75) {
    $(id).addClass("text-info");
    $(id).removeClass("text-success text-warning text-danger");
  } else if(value >= 50) {
    $(id).addClass("text-success");
    $(id).removeClass("text-info text-warning text-danger");
  } else if(value >= 25) {
    $(id).addClass("text-warning");
    $(id).removeClass("text-info text-success text-danger");
  } else {
    $(id).addClass("text-danger");
    $(id).removeClass("text-info text-success text-warning");
  }
};

// function to display information for a new design
function displayDesign(data) {
  // configure user interface components
  $("#design-file").val('');
  $("#design-file").siblings(".custom-file-label").removeClass("selected").html('Choose file');
  $("#design-tab").tab('show');
  $("#upload-modal").modal('hide');
  $("#placeholder").addClass("d-none");
  $("#results").removeClass("d-none");

  // set thumbnail image and caption
  $("#thumbnail").attr("src", "data:image/png;base64," + data.thumbnail);
  $('#thumbnail-caption').text(data.designer + ": " + data.name);

  // set physical properties labels
  $("#physical-mass").text(data.mass.toFixed(2) + ' g');
  $("#physical-volume").text((data.volume).toFixed(1) + ' mL');
  $("#physical-length").text((data.length).toFixed(1) + ' mm');
  $("#physical-wheelbase").text((data.wheelbase).toFixed(1) + ' mm');
  $("#physical-width").text((data.width).toFixed(1) + ' mm');
  $("#physical-track").text((data.track).toFixed(1) + ' mm');
  $("#physical-height").text((data.height).toFixed(1) + ' mm');
  $("#physical-number-seats").text(data.numberSeats);
  $("#physical-cargo-volume").text((data.cargoVolume).toFixed(1) + ' mL');

  // update requirements analysis labels
  updateRequirementsAnalysisLabel(
    "#requirement-bricks",
    data.requirements.isOnlyValidBricks.value,
    data.requirements.isOnlyValidBricks.value ? 'Valid' :
    "Invalid bricks: " + data.requirements.isOnlyValidBricks.invalidBricks.map(function(id) {
      return "<a href='https://www.bricklink.com/v2/catalog/catalogitem.page?P=" + id + "' target='_blank'>" + id + "</a>";
    }).join(", ") + "."
  );
  updateRequirementsAnalysisLabel(
    "#requirement-connected",
    data.requirements.isFullyConnected.value,
    data.requirements.isFullyConnected.value ? 'Valid' :
    data.requirements.isFullyConnected.count + " components detected."
  );
  updateRequirementsAnalysisLabel(
    "#requirement-steering",
    data.requirements.isOneSteeringWheel.value,
    data.requirements.isOneSteeringWheel.value ? 'Valid' :
    data.requirements.isOneSteeringWheel.count + " detected."
  );
  updateRequirementsAnalysisLabel(
    "#requirement-seat",
    data.requirements.isMinOneSeatAligned.value,
    getRequirementsAnalysisDescription(data.requirements.isMinOneSeatAligned, 1)
  );
  updateRequirementsAnalysisLabel(
    "#requirement-wheels",
    data.requirements.isMinFourWheelsAlignedOnBottom.value,
    getRequirementsAnalysisDescription(data.requirements.isMinFourWheelsAlignedOnBottom, 4)
  );
  updateRequirementsAnalysisLabel(
    "#requirement-headlights",
    data.requirements.isMinTwoHeadlightsAlignedOnFront.value,
    getRequirementsAnalysisDescription(data.requirements.isMinTwoHeadlightsAlignedOnFront, 2)
  );
  updateRequirementsAnalysisLabel(
    "#requirement-taillights",
    data.requirements.isMinTwoTaillightsAlignedOnBack.value,
    getRequirementsAnalysisDescription(data.requirements.isMinTwoTaillightsAlignedOnBack, 2)
  );
  updateRequirementsAnalysisLabel(
    "#requirement-plate",
    data.requirements.isOneLicensePlateAlignedOnBack.value,
    getRequirementsAnalysisDescription(data.requirements.isOneLicensePlateAlignedOnBack, 1)
  );

  // update cost analysis labels
  $("#cost-materials").text('$' + data.cost.materials.toFixed(2));
  $("#cost-materials-collapse").html(
    Object.keys(data.cost.bom).map(function(id) {
        return "<div class='row text-secondary'><div class='col-9'>"
          + data.cost.bom[id].name
          + " ("
          + data.cost.bom[id].quantity
          + " x $"
          + data.cost.bom[id].cost.toFixed(3)
          + ")</div><div class='col-3'>$"
          + (data.cost.bom[id].cost*data.cost.bom[id].quantity).toFixed(2)
          + "</div></div>";
      }
    ).join('')
  );
  $("#cost-assembly").text('$' + data.cost.assembly.total.toFixed(2));
  $("#cost-assembly-components").text("$" + data.cost.assembly.components.toFixed(2));
  $("#cost-assembly-integration").text("$" + data.cost.assembly.integration.toFixed(2));
  $("#cost-overhead").text("$" + data.cost.overhead.total.toFixed(2));
  $("#cost-overhead-marketing").text("$" + data.cost.overhead.marketing.toFixed(2));
  $("#cost-overhead-engineering").text("$" + data.cost.overhead.engineering.toFixed(2));
  $("#cost-overhead-facilities").text("$" + data.cost.overhead.facilities.toFixed(2));
  $("#cost-overhead-administration").text("$" + data.cost.overhead.administration.toFixed(2));
  $("#cost-total").text('$' + data.cost.total.toFixed(2));

  // update market analysis labels
  updateMarketAnalysisLabel("#value-passenger", data.value.passenger);
  updateMarketAnalysisLabel("#value-cargo", data.value.cargo);
  updateMarketAnalysisLabel("#value-handling", data.value.handling);
  updateMarketAnalysisLabel("#value-acceleration", data.value.acceleration);
  updateMarketAnalysisLabel("#value-safety", data.value.safety);
  updateMarketAnalysisLabel("#value-coolness", data.value.coolness);
  updateMarketAnalysisLabel("#value-total", data.value.total);
  $("#value-price").text("$" + data.value.price.toFixed(2));

  // update dsm analysis
  var content = "<thead><tr><td></td>" + data.dsm.order.map(
      function(order, index){
        return "<th scope='col' class='text-center' style='width:2em;'><abbr title='"
            + data.dsm.labels[order]
            + "'>"
            + (index + 1)
            + "</abbr></th>";
        }
    ).join() + "</th><tr></thead><tbody>";
  for(var i = 0; i < data.dsm.order.length; i++) {
    content += "<tr scope='row' class='text-center'><th class='text-right'>"
        + (i+1)
        + ":&nbsp;"
        + data.dsm.labels[data.dsm.order[i]].replace(" ", "&nbsp;")
        + "</th>"
        + data.dsm.order.map(
          function(order, index) {
            if(data.dsm.order[i] == order) {
              return "<td class='bg-secondary text-secondary'>1</td>";
            } else if(data.dsm.matrix[data.dsm.order[i]][order]) {
              return "<td class='bg-dark text-dark'>1</td>";
            } else {
              return "<td class='text-white'>0</td>";
            }
          }
      ).join() + "</tr>";
  }
  content += "</tbody>";
  $("#dsm").html(content);
};

// helper function get an url parameter (e.g., /?id=the-design-id)
// https://stackoverflow.com/questions/19491336/how-to-get-url-parameter-using-jquery-or-plain-javascript
function getUrlParameter(sParam) {
  var sPageURL = window.location.search.substring(1),
    sURLVariables = sPageURL.split('&'),
    sParameterName,
    i;
  for (i = 0; i < sURLVariables.length; i++) {
    sParameterName = sURLVariables[i].split('=');
    if (sParameterName[0] === sParam) {
      return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
    }
  }
};

// function to initialize the page after a user login
function initializePage(user) {
  // configure user interface components
  $("#login-modal").modal("hide");
  $("#login-link").hide();
  $("#logout-link").show();
  $("#user-name").text(user.name);
  $("#home-tab").off("hide.bs.tab");

  $("#design-file").on("change", function() {
    var file = this.files[0];
    $(this).siblings(".custom-file-label").addClass("selected").html(file.name);
    if(/(?:\.([^.]+))?$/.exec(file.name)[1] != "io") {
     $("#upload-message").text("Please select a .io file.");
    } else if (file.size > 10*1024*1024) {
      $("#upload-message").text("Max upload size is 10 MB.");
    } else {
      $("#upload-message").text('');
      $.ajax({
        url: 'designs/',
        type: 'POST',
        data: new FormData($('#upload-design-form')[0]),
        cache: false,
        contentType: false,
        processData: false,
        xhr: function () {
          var myXhr = $.ajaxSettings.xhr();
          if (myXhr.upload) {
            myXhr.upload.addEventListener('progress', function (e) {
              if (e.lengthComputable) {
                var progress = e.loaded/e.total*100;
                if(progress > 0 && progress < 100) {
                  $('#upload-progress').removeClass('d-none');
                } else {
                  $('#upload-progress').addClass('d-none');
                }
                $('#upload-progress').css('width', progress + '%').attr('aria-valuenow', progress);
              }
            }, false);
          }
          return myXhr;
        },
        success: displayDesign
      });
    }
  });

  // create a new chart
  var chart = createChart(displayDesign);

  // create a new datatable
  var dataTable = createDataTable(user, chart);
  $("#tradespace-valid").change(function() {
    dataTable.column(4).search($(this).is(":checked")).draw();
  });
  // bind events to trigger datatable re-draw
  $('#tradespace-tab').on('shown.bs.tab', dataTable.draw);
  $('#refresh-tradespace').on('click', dataTable.draw);

  // display design if id parameter is present (e.g., /?id=the-design-id)
  if(getUrlParameter('id')) {
    $.ajax({
      method: "GET",
      url: 'designs/' + getUrlParameter('id'),
      success: displayDesign
    });
  }
};

// helper function to determine if a user is logged in
function getUserInformation() {
  // perform get request
  $.get("/users/me")
  .done(initializePage)
  .fail(function() {
    // if failed, show the login link
    $("#login-link").show();
    $("#logout-link").hide();
    $("#user-name").text("");
    // configure login modal to show when navigating from home tab
    $('#home-tab').on('hide.bs.tab', function (e) {
      $("#login-modal").modal("show");
    });
  });
}

$(document).ready(function() {
  // set up tooltips
  $('[data-toggle="tooltip"]').tooltip();
  // set download links
  $(".palette-link").attr('href', paletteXML);
  $(".modela-link").attr('href', modelaIO);
  // configure links to change tabs
  $(".design-tab-link").on("click", function(e) {
    $("#design-tab").tab("show");
  });
  $(".tradespace-tab-link").on("click", function(e) {
    $("#tradespace-tab").tab("show");
  });
  // set up auto-generated callbacks to display designs
  $(document).on('click', '.design-link', function() {
    $.ajax({
      method: "GET",
      url: 'designs/' + $(this).attr("data-id"),
      success: displayDesign
    });
  });
  // set up auto-generated callbacks to delete designs
  $(document).on('click', '.delete-button', function() {
    if(confirm("Delete design " + $(this).attr("data-id") + "?")) {
      $.ajax({
        method: "DELETE",
        url: 'designs/' + $(this).attr("data-id"),
        success: $('#tradespace-table').DataTable().draw
      });
    }
  });

  // behavior when the login form is submitted
  $("#login-form").on("submit", function(e) {
    // reset error messages
    $("#login-email-message").text("");
    $("#login-passcode-message").text("");
    // try to login
    $.post("/login", $(this).serialize())
    .done(getUserInformation)
    .fail(function() {
      // try to register a new account
      $.ajax({
        type: "POST",
        url: "/register",
        data: JSON.stringify({
          email: $("#login-email").val(),
          password: $("#login-passcode").val(),
          passcode: $("#login-passcode").val()
        }),
        contentType: "application/json"
      }).done(function() {
        // if successful, login again
        $("#login-form").submit();
      }).fail(function(xhr, text, error) {
        // if failed, display error message
        if(xhr.status == 422) {
          $("#login-email-message").text("Invalid email.");
        } else if(xhr.status == 400) {
          $("#login-passcode-message").text("Incorrect passcode.");
        }
      });
    });
    return false;
  });

  // behavior when the logout link is clicked
  $("#logout-link").click(function() {
    $.post("/logout").done(function(){
      // destroy chart
      Chart.getChart('tradespace-chart').destroy();
      // remove datatable callbacks and destroy datatable
      $('#tradespace-tab').off('shown.bs.tab');
      $('#refresh-tradespace').off('click');
      $('#tradespace-table').DataTable().destroy();
      // show home tab and reset user information
      $('#home-tab').tab("show");
      getUserInformation();
    });
  });

  // configure login modal dialog
  $("#login-modal").modal({
    backdrop: "static",
    keyboard: false,
    show: false
  });

  // check if the user is logged in
  getUserInformation();
});
