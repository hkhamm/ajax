/**
 * ACP Brevet Time Calculator javascript
 * @author H. Keith Hamm
 * @date: Fall 2015
 */

var calc = {};

calc.distanceSelector = $('#brevetDistance');
calc.startDateField = $('#startDate');
calc.startTimeField = $('#startTime');
calc.startOpenField = $('#startOpenField');
calc.startCloseField = $('#startCloseField');
calc.checkpointField = $('input[name="checkpoint"]');
calc.addButton = $('.btn-add');
calc.removeButtom = $('.btn-remove');

calc.isNewSession = true;
calc.checkpoints = [];
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

  if (!Number.isInteger(checkpoint) &&
      !$('#alert_placeholder').find('#checkpointAlert' + num).length) {
    calc.alert('Checkpoint '+ num + '\'s distance is invalid.' +
      ' It must be a number and within the valid distance interval.',
      'checkpointAlert' + num);
      // highlight bad fields?
  }

  // TODO validate checkpoint distance

  // AJAX request
  $.getJSON($SCRIPT_ROOT + '/_calc_date_times', {
    checkpoint: checkpoint,
    distance: distance,
    startDate: startDate,
    startTime: startTime
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
        calc.setStartOpenClose(data.start_date, data.start_time,
          data.start_close_time);
      } else if (checkpoint === '') {
        openField.val('Open time');
        closeField.val('Close time');
      }

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

    if (startDate !== '' && startTime !== '') {
      calc.setStartOpenClose(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate === '' && startTime !== '') {
      calc.startTimeField.val(data.start_date);
      calc.setStartOpenClose(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate !== '' && startTime === '') {
      calc.startTimeField.val(data.start_time);
      calc.setStartOpenClose(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate === '' && startTime === '') {
      calc.setStartOpenClose('', '');
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
  for (var i = 0; calc.checkpoints[i] !== undefined; i++) {
    calc.setCheckpoint(calc.checkpoints[i]);
  }
};

/**
 * Adds a checkpoint to the {@checkpoints} array.
 * @checkpoint {object} The checkpoint to add.
 */
calc.addCheckpoint = function(checkpoint) {
  var num = checkpoint.parents('.form-group').find('.checkpoint-label').text();
  num =  num.split(' ')[1].split(':')[0];

  calc.checkpoints[num - 2] = checkpoint;
};

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

  //console.log('startDate change ' + startDate);
  calc.setStartDateTime(startDate, startTime);
});

/**
 * Listens for changes to the Starting Time field. Sets the starting
 * checkpoint's open and close times.
 */
calc.startTimeField.change(function() {
  var startDate = calc.startDateField.val();
  var startTime = $(this).val();

  //console.log('startTime change ' + startTime);
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
calc.addButton.on('click', function(e) {
  e.preventDefault();

  calc.checkpointCount += 1;
  var num = calc.checkpointCount + 1;

  //console.log('add ' + calc.checkpointCount);

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
  //calc.checkpointField = $('input[name="checkpoint"]');
});

/**
 * Listens for clicks on the remove checkpoint button.
 */
calc.removeButtom .on('click', function(e) {
  $('.entry:last').remove();

  calc.checkpointCount -= 1;

  //console.log('remove ' + calc.checkpointCount);

  if (calc.checkpointCount <= 1) {
    $(this).attr('disabled', 'disabled')
  }

  //calc.checkpointField = $('input[name="checkpoint"]');

  e.preventDefault();
  return false;
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
