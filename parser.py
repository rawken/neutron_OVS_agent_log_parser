import argparse
import datetime
import re

TRACE_COUNT = 0
DEBUG_COUNT = 0
INFO_COUNT = 0
WARNING_COUNT = 0
ERR_COUNT = 0
COUNT_ARR = [TRACE_COUNT, DEBUG_COUNT, INFO_COUNT, WARNING_COUNT, ERR_COUNT]

def valid_datetime(input_time):
	try:
		return datetime.datetime.strptime(input_time, '%Y-%m-%d %H:%M:%S') 
	except ValueError:
		message = 'Given datetime is not valid (expected format - \'YYYY-MM-DD HH:mm:ss\')'
		raise argparse.ArgumentTypeError(message)

def argument_parser():
	parser = argparse.ArgumentParser(description='Neutron OVS agent log parser')
	parser.add_argument('-t', '--time',
		nargs=2,
		help='display tracebacks in specific time interval, '
		 	'input format: \'YYYY-MM-DD HH:mm:ss\' \'YYYY-MM-DD HH:mm:ss\'',
		type=valid_datetime)
	parser.add_argument('-f', '--file',
		required=True,
		help='log file',
		type=str)
	return parser.parse_args()

input_args = argument_parser()

if vars(input_args)['time'] == None:
	is_time_arg = False
else:
	start_time = vars(input_args)['time'][0]
	end_time = vars(input_args)['time'][1]
	if start_time > end_time:
		message = 'End time must be greater then start time'
		raise ValueError(message)
	is_time_arg = True

def data_extract():
	result_data = []
	regexpr = re.compile(
		r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})(\s\d*\s)(ERROR|WARNING|INFO)')
	#regexp returns YYYY-DD-MM HH-mm-ss.fff NUMBER LOG_LEVEL

	with open(vars(input_args)['file'], 'r') as log_file:
		for line in log_file:
			result_data.append((re.match(regexpr, line)).groups())

	return (set(result_data))

def tracebacks_counter(COUNT_ARR):
	result_data = data_extract()
	if not is_time_arg:
		for elem in result_data:
			if elem[2] == 'TRACE':
				COUNT_ARR[0] += 1
			elif elem[2] == 'DEBUG':
				COUNT_ARR[1] += 1
			elif elem[2] == 'INFO':
				COUNT_ARR[2] += 1
			elif elem[2] == 'WARNING':
				COUNT_ARR[3] += 1
			elif elem[2] == 'ERROR':
				COUNT_ARR[4] += 1

	else:
		for elem in result_data:
			tmp_date = datetime.datetime.strptime(elem[0], '%Y-%m-%d %H:%M:%S.%f')
			if tmp_date > start_time and tmp_date < end_time:
				if elem[2] == 'TRACE':
					COUNT_ARR[0] += 1
				elif elem[2] == 'DEBUG':
					COUNT_ARR[1] += 1
				elif elem[2] == 'INFO':
					COUNT_ARR[2] += 1
				elif elem[2] == 'WARNING':
					COUNT_ARR[3] += 1
				elif elem[2] == 'ERROR':
					COUNT_ARR[4] += 1
	return COUNT_ARR

def print_res(COUNT_ARR):
	print('Traces - {}\nDebugs - {}\nInfos - {}\n'
		'Warnings - {} \nErrors - {}'.format(*tracebacks_counter(COUNT_ARR)))

def html_res(COUNT_ARR):
	with open('parse_result.html', 'w') as parse_result:
		if not is_time_arg:
			log_time = 'full time'
		else:
			log_time = 'From ' + start_time.strftime('%Y-%m-%d %H:%M:%S') + ' to ' + \
				  end_time.strftime('%Y-%m-%d %H:%M:%S')
		parse_result.write(
		'<head> \n'
    	'	<title>Log parse result</title> \n'
    	'	<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> \n'
  		'	<script src="https://cdnjs.cloudflare.com/ajax/libs/numeric/1.2.6/numeric.min.js"></script>\n'
		'</head>\n'
		'<body>\n'
  		'	<h2>{0}</h2>\n'
  		'	<h3>Time interval: {6}</h3>'
  		'	<ul><li> Traces - {1}</li>\n'
  		'		<li> Debugs - {2}</li>\n'
  		'		<li> Infos - {3}</li>\n'
  		'		<li> Warnings - {4}</li>\n'
  		'		<li> Errors - {5}</li>\n'		
  		'	<div id="myDiv"></div>\n'
  		'	<script>\n'
    	'		var data = [{{\n'
        '			values: [{1}, {2}, {3}, {4}, {5}],\n'
        '			labels: [\'Traces\', \'Debugs\', \'Infos\', \'Warnings\', \'Errors\'],\n'
        '			type: \'pie\'\n'
    	'		}}];\n'
    	'		Plotly.newPlot(\'myDiv\', data);\n'
  		'	</script>\n'
		'</body>'.format(vars(input_args)['file'],
						*COUNT_ARR, log_time)
		)

print_res(COUNT_ARR)
html_res(COUNT_ARR)