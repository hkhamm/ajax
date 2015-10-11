/**
 * ACP Brevet Time Calculator javascript
 * @author H. Keith Hamm
 * @date: Fall 2015
 */

var calc = {};

calc.distanceDropdown = $('#distances').find('li');
calc.startDateField = $('input[name="startDate"]');
calc.startTimeField = $('input[name="startTime"]');
calc.startOpenField = $('span[name="startOpenField"]');
calc.startCloseField = $('span[name="startCloseField"]');
calc.checkpointField = $('input[name="checkpoint"]');

calc.defaultStartDate = moment().add(1, 'd').format('YYYY/MM/DD');
calc.defaultStartTime = '12:00';
calc.isNewSession = true;
calc.checkpoints = [];

/**
 * Sets a checkpoint's open and close datetimes.
 */
calc.setDatetimes = function(that) {
  var openField = that.parents('.row').find('.openField');
  var closeField = that.parents('.row').find('.closeField');

  var distance = $('span[name="distance"]').text();
  var startDate = calc.startDateField.val();
  var startTime = calc.startTimeField.val();
  var checkpoint = that.val();

  // TODO validate checkpoint distance

  // AJAX request
  $.getJSON($SCRIPT_ROOT + '/_calc_date_times', {
    checkpoint: checkpoint,
    distance: distance,
    startDate: startDate,
    startTime: startTime
  }, function(data) {
    calc.addCheckpoint(that);

    if (calc.isNewSession) {
      calc.isNewSession = false;
      calc.setStartDatetimes(data.start_date, data.start_time,
        data.start_close_time);
    } else if (checkpoint === '') {
      openField.val('Open time');
      closeField.val('Close time');
    }

    startDate = calc.startDateField.val();
    startTime = calc.startTimeField.val();

    if (startDate === '' || startTime === '') {
      if (startDate === '' && startTime === '') {
        calc.startDateField.val(data.start_date);
        calc.startTimeField.val(data.start_time);
      } else if (startDate === '') {
        calc.startDateField.val(data.start_date);
      } else if (startTime === '') {
        calc.startTimeField.val(data.start_time);
      }
    }

    openField.text(data.open_time);
    closeField.text(data.close_time);
  });
};

/**
 * Sets the starting checkpoint's open and close fields.
 */
calc.setStartDatetimes = function(startDate, startTime, startCloseTime) {
  calc.startOpenField.text(startDate + ' ' + startTime);
  calc.startCloseField.text(startDate + ' ' + startCloseTime);
};

/**
 * Resets all currently set checkpoints' open and close fields.
 */
calc.setCheckpointDatetimes = function() {
  for (var i = 0; calc.checkpoints[i] !== undefined; i++) {
    calc.setDatetimes(calc.checkpoints[i]);
  }
};

/**
 * Gets a checkpoint's number.
 * @checkpoint {object} The checkpoint to use.
 * @return {number} The checkpoint's number.
 */
calc.getCheckpointNum = function(checkpoint) {
  var num = checkpoint.parents('.row').find('.number').text();
  return num.split(' ')[1].split(':')[0];
};

/**
 * Adds a checkpoint to the {@checkpoints} array.
 * @checkpoint {object} The checkpoint to add.
 */
calc.addCheckpoint = function(checkpoint) {
  var num = calc.getCheckpointNum(checkpoint);
  calc.checkpoints[num - 2] = checkpoint;
};

/**
 * Listens for changes to the brevet distance. Sets the distance field on
 * selection.
 */
calc.distanceDropdown.on('click', function() {
  var distance_field = $(this).parents('.row').find('.distance_field');
  distance_field.text($(this).text());
});

/**
 * Listens for changes to the Starting Date field. Sets the
 * starting checkpoint's open and close times.
 */
calc.startDateField.change(function() {
  var startDate = $(this).val();
  var startTime = calc.startTimeField.val();

  //console.log('startDate change');
  //console.log('isNewSession: ' + calc.isNewSession);
  //console.log('startDate: ' + startDate);
  //console.log('startTime: ' + startTime);
  //console.log('---');

  // TODO validate start date

  // AJAX request
  $.getJSON($SCRIPT_ROOT + '/_get_start_date_times', {
    startDate: startDate,
    startTime: startTime
  }, function(data) {
    if (startDate !== '' && startTime !== '') {
      calc.setStartDatetimes(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate !== '' && startTime === '') {
      calc.startTimeField.val(data.start_time);
      calc.setStartDatetimes(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate === '' && startTime === '') {
      calc.setStartDatetimes('Open time (Start)', 'Close time (Start)');
    }

    calc.setCheckpointDatetimes();
  });
});

/**
 * Listens for changes to the Starting Time field. Sets the starting
 * checkpoint's open and close times.
 */
calc.startTimeField.change(function() {
  var startDate = calc.startDateField.val();
  var startTime = $(this).val();

  //console.log('startTime change');
  //console.log('isNewSession: ' + calc.isNewSession);
  //console.log('startDate: ' + startDate);
  //console.log('startTime: ' + startTime);
  //console.log('---');

  // TODO validate start time

  // AJAX request
  $.getJSON($SCRIPT_ROOT + '/_get_start_date_times', {
    startDate: startDate,
    startTime: startTime
  }, function(data) {
    if (startDate !== '' && startTime !== '') {
      calc.setStartDatetimes(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate === '' && startTime !== '') {
      calc.startTimeField.val(data.start_date);
      calc.setStartDatetimes(startDate, startTime, data.start_close_time);
    } else if (!calc.isNewSession && startDate === '' && startTime === '') {
      calc.setStartDatetimes('Open time (Start)', 'Close time (Start)');
    }

    calc.setCheckpointDatetimes();
  });
});

/**
 * Listens for changes to checkpoint distance fields.
 */
calc.checkpointField.change(function() {
  calc.setDatetimes($(this));
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
