/**
 * ACP Brevet Time Calculator javascript
 * @author H. Keith Hamm
 * @date: Fall 2015
 */

// TODO handle output miles on text document
// TODO handle custom output dates everywhere?
// TODO write unit tests
// TODO last checkpoint between the brevet distance and that distance plus 10%

var calc = {};

calc.distanceSelector = $('#brevetDistance');
calc.startDateField = $('#startDate');
calc.startTimeField = $('#startTime');
calc.startOpenField = $('#startOpenField');
calc.startCloseField = $('#startCloseField');
calc.checkpointField = $('input[name="checkpoint"]');
calc.checkpoint2Open = $('#openField');
calc.checkpoint2Close = $('#closeField');
calc.addButton = $('.btn-add');
calc.removeButton = $('.btn-remove');
calc.textButton = $('#textButton');

calc.isNewSession = true;
calc.checkpoints = [];
calc.checkpointVals = [];
calc.openTimes = [];
calc.closeTimes = [];
calc.checkpointCount = 1;

/**
 * Sets a checkpoint's open and close datetimes.
 */
calc.setCheckpoint = function(that) {
  var openField = that.parents('.form-group').find('#openField');
  var closeField = that.parents('.form-group').find('#closeField');

  var distance = $("#brevetDistance option:selected").val();
  var startDate = calc.startDateField.val();
  var startTime = calc.startTimeField.val();
  var checkpoint = that.val();
  var num = calc.checkpointCount + 1;
  var units = $('#units input:radio:checked').val();
  var dates = $('#dates input:radio:checked').val();

  var len = checkpoint.length;
  for (var i = 0; i < len; i++) {
    if (isNaN(parseInt(checkpoint.charAt(i))) &&
        !$('#alert_placeholder').find('#checkpointAlert' + num).length) {
      calc.alert('Checkpoint '+ num + '\'s distance is invalid.' +
      ' It must be a number and within the valid distance interval.',
      'checkpointAlert' + num);
      // highlight bad fields?
      break;
    }
  }

  $.getJSON($SCRIPT_ROOT + '/_calc_date_times', {
    checkpoint: checkpoint,
    distance: distance,
    startDate: startDate,
    startTime: startTime,
    units: units,
    dates: dates
  }, function(data) {
    if (!data.is_valid_checkpoint &&
        !$('#alert_placeholder').find('#checkpointAlert' + num).length) {
      calc.alert('Checkpoint '+ num + '\'s distance is invalid.' +
        ' It must be a number and within the valid distance interval.',
        'checkpointAlert' + num);
        // highlight bad fields?
    } else {
      calc.addCheckpoint(that);

      if (calc.isNewSession) {
        calc.isNewSession = false;
      } else if (checkpoint === '') {
        openField.val('Open time');
        closeField.val('Close time');
      }

      calc.setStartOpenClose(data.start_open_date, data.start_time,
          data.start_close_time);

      startDate = calc.startDateField.val();
      startTime = calc.startTimeField.val();

      if (startDate === '') {
        calc.startDateField.val(data.start_date);
      }

      if (startTime === '') {
        calc.startTimeField.val(data.start_time);
      }

      openField.val(data.open_time);
      closeField.val(data.close_time);
    }
  });
};

/**
 * Sets the starting date and time fields.
 */
calc.setStartDateTime = function(startDate, startTime) {
  // AJAX request
  $.getJSON($SCRIPT_ROOT + '/_get_start_date_times', {
    startDate: startDate,
    startTime: startTime
  }, function(data) {

    var isValidDate = data.is_valid_date;
    var isValidTime = data.is_valid_time;

    if (!isValidDate || !isValidTime) {
      if (!isValidDate &&
          !$('#alert_placeholder').find('#startDateAlert').length) {
        calc.alert('The Starting Date you entered is invalid. It must have' +
          ' this form: YYYY/MM/DD', 'startDateAlert');
        // highlight bad fields?
      }
      if (!isValidTime &&
          !($('#alert_placeholder').find('startTimeAlert').length)) {
        calc.alert('The Starting Time you entered is invalid. It must be' +
        ' in 24 format and have this form: HH:mm', 'startTimeAlert');
      }
      // highlight bad fields?
      return
    }

    calc.resetCheckpoints();
  });
};

/**
 * Sets the starting checkpoint's open and close fields.
 */
calc.setStartOpenClose = function(startDate, startTime, startCloseTime) {
  calc.startOpenField.val(startDate + ' ' + startTime);
  calc.startCloseField.val(startDate + ' ' + startCloseTime);
};

/**
 * Resets all currently set checkpoints' open and close fields.
 */
calc.resetCheckpoints = function() {
  var length = calc.checkpoints.length;
  for (var i = 0; i < length; i++) {
    if (calc.checkpoints[i] !== undefined) {
      calc.setCheckpoint(calc.checkpoints[i]);
    }
  }
};

/**
 * Adds a checkpoint to the {@checkpoints} array.
 * @checkpoint {object} The checkpoint to add.
 */
calc.addCheckpoint = function(checkpoint) {
  var num = checkpoint.parents('.form-group').find('.checkpoint-label').text();
  num = num.split(' ')[1].split(':')[0];

  calc.checkpoints[num - 2] = checkpoint;
};

/**
 * Gets a checkpoint's number.
 * @checkpoint {object} The checkpoint.
 */
calc.getCheckpointNum = function(checkpoint) {
  var num = checkpoint.parents('.form-group').find('.checkpoint-label').text();
  return num.split(' ')[1].split(':')[0];
};

/**
 * Creates a Bootstrap alert.
 * @message {string} The alert message.
 * @alert_type {string) The alert type.
 */
calc.alert = function(message, alert_type) {
  var alertMsg = '<div class="alert alert-warning alert-dismissible" \
  role="alert" id="' + alert_type + '"><button type="button" class="close" \
  data-dismiss="alert"aria-label="Close"><span aria-hidden="true">&times;\
  </span></button><strong>Warning!</strong> ' + message + '</div>';

  $('#alert_placeholder').append(alertMsg);
};

/**
 * Listens for changes to the Starting Date field. Sets the
 * starting checkpoint's open and close times.
 */
calc.startDateField.change(function() {
  var startDate = $(this).val();
  var startTime = calc.startTimeField.val();

  calc.setStartDateTime(startDate, startTime);
});

/**
 * Listens for changes to the Starting Time field. Sets the starting
 * checkpoint's open and close times.
 */
calc.startTimeField.change(function() {
  var startDate = calc.startDateField.val();
  var startTime = $(this).val();

  calc.setStartDateTime(startDate, startTime);
});

/**
 * Listens for changes to checkpoint distance fields.
 */
$('#checkpoint').change(function() {
  calc.setCheckpoint($(this));
});

/**
 * Listens for clicks on the add checkpoint button.
 */
calc.addButton.click(function(e) {
  e.preventDefault();

  calc.checkpointCount += 1;
  var num = calc.checkpointCount + 1;

  if (calc.checkpointCount > 1) {
    $('.btn-remove').removeAttr('disabled');
  }

  var controlForm = $('.checkpoints div:first'),
      currentEntry = $('.entry:first'),
      newEntry = $(currentEntry.clone()).appendTo(controlForm);

  newEntry.find('input').val('');
  newEntry.find('.checkpoint-label').text('Checkpoint ' + num);
  controlForm.find('.entry:not(:last)');

  newEntry.find('#checkpoint').change(function() {
    calc.setCheckpoint($(this));
  });
});

/**
 * Listens for clicks on the remove checkpoint button.
 */
calc.removeButton.click(function(e) {
  $('.entry:last').remove();

  calc.checkpointCount -= 1;

  if (calc.checkpointCount <= 1) {
    $(this).attr('disabled', 'disabled')
  }

  e.preventDefault();
  return false;
});

calc.textButton.click(function() {
  var brevetDistance = $("#brevetDistance option:selected").val();
  var startDate = calc.startDateField.val();
  var startTime = calc.startTimeField.val();
  var startOpen = calc.startOpenField.val();
  var startClose = calc.startCloseField.val();
  var units = $('#units input:radio:checked').val();
  var dates = $('#dates input:radio:checked').val();
  var checkpointDistances = [];
  var openTimes = [];
  var closeTimes = [];

  var that;
  var openField;
  var closeField;
  var i;
  var length = calc.checkpoints.length;

  for (i = 0; i < length; i++) {
    if (calc.checkpoints[i] !== undefined) {
      that = calc.checkpoints[i];
      openField = that.parents('.form-group').find('#openField');
      closeField = that.parents('.form-group').find('#closeField');

      checkpointDistances[i] = that.val();
      openTimes[i] = openField.val();
      closeTimes[i] = closeField.val();
    }
  }

  console.log(JSON.stringify(checkpointDistances));

  $.getJSON($SCRIPT_ROOT + '/_create_times', {
    brevetDistance: brevetDistance,
    startDate: startDate,
    startTime: startTime,
    startOpen: startOpen,
    startClose: startClose,
    units: units,
    dates: dates,
    checkpointDistances: JSON.stringify(checkpointDistances),
    openTimes: JSON.stringify(openTimes),
    closeTimes: JSON.stringify(closeTimes)
  });
  window.open('/times');
});

$('#dates input:radio').change(function() {
  console.log('date format change');
  calc.resetCheckpoints();
});


//$(document).ready(function(){
//// Do the following when the page is finished loading
//
//   // When a field named 'miles' is changed ...
//   $('input[name="miles"]').change(
//       // ... execute this function
//       function(){
//           var e_miles = $(this).val();
//
//           var target = $(this).parents(".row").find(".times");
//
//           // DEBUG: How do I replace the 'times' field?
//           // alert("Content of the field I want to change: " +
//           //   target.html());
//
//           // AJAX request
//           $.getJSON($SCRIPT_ROOT + '/_calc_times',
//               // The object to pass to the server
//               { miles: e_miles },
//               // The function to call with the response
//               function(data) {
//                  var times = data.result;
//                  // alert("Got a response: " +  times);
//                  target.text(times);
//               }); // End of the call to getJSON
//       });  // End of the function to be called when field changes
//});   // end of what we do on document ready
