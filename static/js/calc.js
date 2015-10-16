/**
 * ACP Brevet Time Calculator javascript
 * @author H. Keith Hamm
 * @date: Fall 2015
 */

var calc = {};

// jQuery HTML elements
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
calc.alert_placeholder = $('#alert_placeholder');

// Printing variables
calc.checkpointVals = [];
calc.openTimes = [];
calc.closeTimes = [];

calc.isNewSession = true;
calc.checkpoints = [];
calc.checkpointCount = 1;
calc.units = 'km';

// TODO look at everything that deals with validation and see if it works
// TODO ^ with miles

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

  calc.checkpointVals[num - 1] = that.val();

  calc.checkForMultiFinals(checkpoint, distance, num - 1);

  calc.checkForLetters(checkpoint, num);

  calc.checkOrder(checkpoint, num);

  $.getJSON($SCRIPT_ROOT + '/_calc_date_times', {
    checkpoint: checkpoint,
    distance: distance,
    startDate: startDate,
    startTime: startTime,
    units: units,
    dates: dates
  }, function(data) {
    if (calc.isValidDistance(data, num)) {
      calc.checkForFinalCheckpoint(checkpoint, distance, num);

      calc.addCheckpoint(that);

      if (calc.isNewSession) {
        calc.isNewSession = false;
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

      if (checkpoint === '') {
        openField.val('Open time');
        closeField.val('Close time');
      } else {
        openField.val(data.open_time);
        closeField.val(data.close_time);
      }
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
          !calc.alert_placeholder.find('#startDateAlert').length) {
        calc.alert('The Starting Date you entered is invalid. It must have' +
          ' this form: YYYY/MM/DD', 'startDateAlert');
        // highlight bad fields?
      }
      if (!isValidTime &&
          !(calc.alert_placeholder.find('startTimeAlert').length)) {
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
 * @param checkpoint The checkpoint to add.
 */
calc.addCheckpoint = function(checkpoint) {
  var num = checkpoint.parents('.form-group').find('.checkpoint-label').text();
  num = num.split(' ')[1].split(':')[0];

  calc.checkpoints[num - 2] = checkpoint;
};

/**
 * Checks if the new checkpoint has letters instead of numbers in the distance.
 * @param checkpoint is the new checkpoint's distance.
 * @param num is the new checkpoint's number.
 */
calc.checkForLetters = function(checkpoint, num) {
  var len = checkpoint.length;
  for (var i = 0; i < len; i++) {
    if (isNaN(parseInt(checkpoint.charAt(i))) &&
        !calc.alert_placeholder.find('#checkpointAlert' + num).length) {
      calc.alert('Checkpoint '+ num + '\'s distance is invalid.' +
      ' It must be a number and within the valid distance interval.',
      'checkpointAlert' + num);
      // highlight bad fields?
      break;
    }
  }
};

/**
 * Checks for a final checkpoint and hides or shows the message.
 * @param checkpoint is the new checkpoint's distance.
 * @param distance is the brevet distance.
 * @param num is the new checkpoint's number.
 */
calc.checkForFinalCheckpoint = function(checkpoint, distance, num) {
  if (calc.units === 'miles') {
    var conv_fac = 0.621371;
    checkpoint /= conv_fac;
    distance /= conv_fac;
  } else {
    checkpoint = parseInt(checkpoint);
    distance = parseInt(distance);
  }

  if (checkpoint >= distance) {
    $('.final-checkpoint-message').hide();
  } else if (num === calc.checkpointVals.length && checkpoint < distance) {
    $('.final-checkpoint-message').show();
  }
};

/**
 * Check for multiple final checkpoints.
 * @param checkpoint is the new 's checkpoint's distance.
 * @param distance is the brevet distance.
 * @param num is the number of the previous checkpoint.
 */
calc.checkForMultiFinals = function(checkpoint, distance, num) {
  var length = calc.checkpoints.length;

  if (calc.units === 'miles') {
    checkpoint /= 0.621371;
    distance /= 0.621371;
  } else {
    checkpoint = parseInt(checkpoint);
    distance = parseInt(distance);
  }

  for (var i = 0; i < length; i++) {
    if (calc.checkpoints[i] !== undefined) {
      var thisNum = parseInt(calc.getCheckpointNum(calc.checkpoints[i]), 10);
      var thisVal = calc.checkpoints[i].val();

      if (num === thisNum && thisVal >= distance && checkpoint >= distance &&
          !calc.alert_placeholder.find('#checkpointAlert' + num).length) {
        calc.alert('It looks like you may have multiple final checkpoints.',
          'checkpointAlert' + num);
        break;
      }
    }
  }
};

/**
 * Checks the order of checkpoint distances.
 * @param checkpoint is the new 's checkpoint's distance.
 * @param num is the number of the previous checkpoint.
 */
calc.checkOrder = function(checkpoint, num) {
  var thisVal;
  var length = calc.checkpoints.length;

  if (calc.units === 'miles') {
    checkpoint /= 0.621371;
  } else {
    checkpoint = parseInt(checkpoint);
  }

  for (var i = 0; i < length; i++) {
    if (calc.checkpoints[i] !== undefined) {
      if (calc.units === 'miles') {
        thisVal = calc.checkpoints[i].val() / 0.621371;
      } else {
        thisVal = calc.checkpoints[i].val()
      }
      var thisNum = parseInt(calc.getCheckpointNum(calc.checkpoints[i]), 10);

      if ((num - 1) === thisNum && thisVal > checkpoint &&
          !calc.alert_placeholder.find('#orderAlert' + num).length) {
        calc.alert('You need to create checkpoints in ascending order.',
          'orderAlert' + num);
      }
    }
  }
};

/**
 * Checks booleans returned from the server.
 * @param data is the data returns from the server.
 * @param num is the new checkpoint's number.
 * @returns {boolean} true if both checks are true, false if not
 */
calc.isValidDistance = function(data, num) {
  var valid = true;
  if (!data.is_valid_checkpoint &&
      !calc.alert_placeholder.find('#checkpointAlert' + num).length) {
    calc.alert('Checkpoint '+ num + '\'s distance is invalid.' +
      ' It must be a number and within the valid distance interval.',
      'checkpointAlert' + num);
      // highlight bad fields?
    valid = false;
  } else if (data.is_over_10p &&
        !calc.alert_placeholder.find('#finalCheckpointAlert' + num).length) {
    calc.alert('Checkpoint ' + num + '\'s distance is potentially invalid.' +
      ' While checkpoints greater than 20% of the brevet distance can be ok' +
      ', ideally they are no more that 10% greater than the brevet' +
      ' distance.',
      'finalCheckpointAlert' + num);
    valid = false;
  }
  return valid;
};

/**
 * Gets a checkpoint's number.
 * @param checkpoint The checkpoint.
 */
calc.getCheckpointNum = function(checkpoint) {
  var num = checkpoint.parents('.form-group').find('.checkpoint-label').text();
  return num.split(' ')[1].split(':')[0];
};

/**
 * Creates a Bootstrap alert.
 * @param message The alert message.
 * @param alert_type The alert type.
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
 * Listens for changes to the first checkpoint's distance field.
 */
$('#checkpoint').change(function() {
  calc.setCheckpoint($(this));
});

/**
 * Listens for changes to the dates radio buttons.
 */
$('#dates input:radio').change(function() {
  calc.resetCheckpoints();
});

/**
 * Listens for changes to the units radio buttons.
 */
$('#units input:radio').change(function() {
  if (calc.units === 'km') {
    calc.units = 'miles';
  } else {
    calc.units = 'km';
  }
  calc.resetCheckpoints();
});

/**
 * Listens for clicks on the add checkpoint button.
 */
calc.addButton.click(function() {
  calc.checkpointCount += 1;
  var num = calc.checkpointCount + 1;

  if (calc.checkpointCount > 1) {
    $('.btn-remove').removeAttr('disabled');
  }

  var controlForm = $('.checkpoints div:first');
  var currentEntry = $('.entry:first');
  var newEntry = $(currentEntry.clone()).appendTo(controlForm);

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
calc.removeButton.click(function() {
  $('.entry:last').remove();

  calc.checkpointCount -= 1;

  if (calc.checkpointCount <= 1) {
    $(this).attr('disabled', 'disabled')
  }
});

/**
 * Listens for clicks on the generate text button.
 */
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

  $.getJSON($SCRIPT_ROOT + '/_create_text', {
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
  window.open('/text');
});
