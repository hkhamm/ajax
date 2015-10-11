# Tests:

## Action: change start date
- if is_first_run and start_time == '':
      do nothing
- if is_first_run and start_date != '' and start_time != '':
      set starting checkpoint open and close times
- if !is_first_run and start_time == '':
      start_time = default_start_time
      set starting open and close times
- if !is_first_run and start_date != '' and start_time != '':
      set starting checkpoint open and close times

## Action: change start time
- if is_first_run and start_date == '':
      do nothing
- if is_first_run and start_date != '' and start_time != '':
      sets starting open and close times
- if !is_first_run and start_date == '':
      start_date = default_start_date
      sets starting checkpoint open and close times
- if !is_first_run and start_date != '' and start_time != '':
      sets starting checkpoint open and close times

## Action: change checkpoint 2 distance
- if checkpoint 2 distance == '':
      start_open = 'Open time'
      start_close = 'Close time'
- if start_date == '' and start_time == '':
      start_date = default_start_date
      start_time = default_start_time
- if start_date == '':
      start_date = default_start_date
- if start_time == '':
      start_time = default_start_time
- if checkpoint 2 distance != '':
      set starting checkpoint open and close times

## Action: change checkpoint 3-25 distance
- if checkpoint distance == '':
      alert: warn user that checkpoint 1 must be set
- if checkpoint distance != '':
      set checkpoint open and close times
