import argparse
import datetime
import re
import sys

traceback_msgs = ('TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR')
traceback_dict = dict.fromkeys(traceback_msgs, 0)


def validate_datetime(input_time):
    try:
        return datetime.datetime.strptime(input_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        message = 'Given datetime is not valid (expected format - '\
                  '\'YYYY-MM-DD HH:mm:ss\')'
        raise argparse.ArgumentTypeError(message)


def parse_input_arguments():
    parser = argparse.ArgumentParser(
        description='Neutron OVS agent log parser')
    parser.add_argument(
        '-st',
        '--start',
        dest='start',
        type=validate_datetime,
        help='displays tracebacks from the start of log file'
             'till entered date and time'
             'input format: \'YYYY-MM-DD HH:mm:ss\'')
    parser.add_argument(
        '-et',
        '--end',
        type=validate_datetime,
        dest='end',
        help='displays tracebacks from entered date and time'
             'till the end of log file'
             'input format: \'YYYY-MM-DD HH:mm:ss\'')
    parser.add_argument(
        '-f',
        '--file',
        required=True,
        help='path to log file',
        type=str)
    return parser.parse_args()


def find_start_and_end():
    if '-st' and '-et' in sys.argv:
        start_time = input_args.start
        end_time = input_args.end
    elif '-st' and '-et' not in sys.argv:
        start_time = input_args.start
        end_time = None
    elif '-et' and '-st' not in sys.argv:
        start_time = None
        end_time = input_args.end
    else:
        start_time = None
        end_time = None
    return start_time, end_time


def exctract_data(file_name):
    result_data = []
    messages = '(TRACE|DEBUG|ERROR|WARNING|INFO)'
    regexpr = re.compile(
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})(\s\d*\s)' + messages)
    # regexp returns YYYY-DD-MM HH-mm-ss.fff NUMBER LOG_LEVEL

    with open(file_name, 'r') as log_file:
        for line in log_file:
            result_data.append((re.match(regexpr, line)).groups())
    return (set(result_data))


def count_tracebacks(*args):
    result_data = args[0]
    if len(args) == 1:
        for elem in result_data:
            traceback_dict[elem[2]] += 1
    elif len(args) == 3:
        start_time = args[1]
        end_time = args[2]
        for elem in result_data:
            tmp_date = datetime.datetime.strptime(
                    elem[0],
                    '%Y-%m-%d %H:%M:%S.%f')
            if start_time and end_time:
                if tmp_date > start_time and tmp_date < end_time:
                    traceback_dict[elem[2]] += 1
            elif not start_time and tmp_date < end_time:
                traceback_dict[elem[2]] += 1
            elif not end_time and tmp_date > start_time:
                traceback_dict[elem[2]] += 1


def print_result(values_list):
    print('Traces - {traces}\nDebugs - {debugs}\nInfos - {infos}\n'
          'Warnings - {warnings}\nErrors - {errors}'.format(
                                                    traces=values_list[0],
                                                    debugs=values_list[1],
                                                    infos=values_list[2],
                                                    warnings=values_list[3],
                                                    errors=values_list[4]))


def find_parsing_interval(start_time, end_time):
    parsing_interval = 'From start till end of the file'
    if start_time and end_time:
        parsing_interval = 'From ' + \
                           start_time.strftime('%Y-%m-%d %H:%M:%S') + \
                           ' to ' + \
                           end_time.strftime('%Y-%m-%d %H:%M:%S')
    elif start_time and not end_time:
        parsing_interval = 'From ' + \
                           start_time.strftime('%Y-%m-%d %H:%M:%S') + \
                           ' till the end of log'
    elif not start_time and end_time:
        parsing_interval = 'From start of log file till ' + \
                           end_time.strftime('%Y-%m-%d %H:%M:%S')
    return parsing_interval


def generate_html_result(parsing_interval, file_name, values_list):
    with open('parse_result.html', 'w') as parse_result:
        parse_result.write(
        '<head> \n'
        '	<title>Log parse result</title> \n'
        '	<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> \n'
        '	<script src="https://cdnjs.cloudflare.com/ajax/libs/numeric/1.2.6/numeric.min.js"></script>\n'
        '</head>\n'
        '<body>\n'
        '	<h2>{file_name}</h2>\n'
        '	<h3>Time interval: {parsing_interval}</h3>\n'
        '	<ul><li> Traces - {trace_count}</li>\n'
        '		<li> Debugs - {debug_count}</li>\n'
        '		<li> Infos - {info_count}</li>\n'
        '		<li> Warnings - {warning_count}</li>\n'
        '		<li> Errors - {err_count}</li>\n'
        '	<div id="myDiv"></div>\n'
        '	<script>\n'
        '		var data = [{{\n'
        '			values: [{trace_count}, {debug_count}, {info_count}, {warning_count}, {err_count}],\n'
        '			labels: [\'Traces\', \'Debugs\', \'Infos\', \'Warnings\', \'Errors\'],\n'
        '			type: \'pie\'\n'
        '		}}];\n'
        '		Plotly.newPlot(\'myDiv\', data);\n'
        '	</script>\n'
        '</body>'.format(file_name=file_name,
                        trace_count=values_list[0],
                        debug_count=values_list[1],
                        info_count=values_list[2],
                        warning_count=values_list[3],
                        err_count=values_list[4],
                        parsing_interval=parsing_interval)
        )


if __name__ == '__main__':
    input_args = parse_input_arguments()
    file_name = input_args.file

    result_data = exctract_data(file_name)
    start_time, end_time = find_start_and_end()

    if not start_time and not end_time:
        count_tracebacks(result_data)
    else:
        if start_time and end_time:
            if start_time > end_time:
                message = 'End time must be greater then start time'
                raise ValueError(message)
        count_tracebacks(result_data, start_time, end_time)

    values_list = list(traceback_dict.values())
    print_result(values_list)
    generate_html_result(find_parsing_interval(start_time, end_time), file_name, values_list)