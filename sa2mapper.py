import sys
import os
import csv


def sanitize_argument_list(arguments):
    sanitized_arguments = []
    splitted_file_name = None
    for argument in arguments:
        splitted_file_name = argument.split('.')
        if splitted_file_name[-1] != "py":
            sanitized_arguments.append(argument)

    return sanitized_arguments


def are_arguments_valid(sanitized_arguments):
    if len(sanitized_arguments) != 2:
        return False

    if not os.path.isfile('%s/%s' % (os.getcwd(), sanitized_arguments[0])):
        return False

    return True


def generate_error_message(sanitized_arguments):
    if len(sanitized_arguments) != 2:
        return "You did not input 2 arguments to the app"

    if not os.path.isfile('%s/%s' % (os.getcwd(), sanitized_arguments[0])):
        return "The input file you provided doesn't exists"

    return "Something went wrong!"


def init_mapping_dictionary():
    mapping_dictionary = {}
    with open("sa2mappingfile.csv", "r") as mapping_file:
        csv_reader = csv.reader(mapping_file, delimiter=',')
        next(csv_reader)
        old_region_id = None
        new_region_id = None
        weight = None
        current_shapes_array = None
        for lines in csv_reader:
            old_region_id = lines[0]
            new_region_id = lines[1]
            weight = lines[2]
            if mapping_dictionary.get(old_region_id) is None:
                mapping_dictionary.update({old_region_id: [{'region_id': new_region_id, 'weight': weight}]})
            else:
                current_shapes_array = mapping_dictionary.get(old_region_id)
                current_shapes_array.append({'region_id': new_region_id, 'weight': weight})

        return mapping_dictionary


def parse_input_file(input_file):
    with open(input_file, "r") as sa_2011_file:
        csv_reader = csv.reader(sa_2011_file, delimiter=',')
        next(csv_reader)
        return list(csv_reader)


def is_float(number):
    try:
        converted_number = float(number)
    except ValueError:
        return False

    return True


def update_new_format_dictionary(dictionary, sa2_2016_value, data):
    region_id = sa2_2016_value.get('region_id')
    if dictionary.get(region_id) is None:
        sa2_weight = sa2_2016_value.get('weight')
        if not is_float(sa2_weight):
            print('%s cannot be converted to a float' % sa2_weight)
            return
        dictionary.update({region_id: {'region_id': region_id, 'weight': (data * float(sa2_2016_value.get('weight')))}})
    else:
        sa2_weight = sa2_2016_value.get('weight')
        if not is_float(sa2_weight):
            print('%s cannot be converted to a float' % sa2_weight)
            return

        current_format_object = dictionary.get(region_id)
        current_weight = float(current_format_object.get('weight'))
        current_weight += (data * float(sa2_2016_value.get('weight')))
        current_format_object['weight'] = current_weight
        dictionary.update({region_id: current_format_object})


def convert_old_to_new_format(mapping_dictionary, old_format_lines):
    new_format = {}
    region_id = None
    sa2_2016_values = None
    for line in old_format_lines:
        region_id = line[0]
        data_value = line[1]
        if not is_float(data_value):
            print('%s cannot be converted to a float' % data_value)
            continue
        converted_data_value = float(data_value)
        sa2_2016_values = mapping_dictionary.get(region_id)
        for sa2_2016_value in sa2_2016_values:
            update_new_format_dictionary(new_format, sa2_2016_value, converted_data_value)

    return new_format


def write_output(new_format_list, file_name):
    with open(file_name, 'w', newline='\n') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        writer.writerows(new_format_list)


def prepare_input_for_csv(new_format):
    new_format_values = []
    for key in new_format.keys():
        value = new_format.get(key)
        new_format_values.append([value.get('region_id'), value.get('weight')])

    return new_format_values


def main():
    sanitized_arguments = sanitize_argument_list(sys.argv)
    if not are_arguments_valid(sanitized_arguments):
        sys.exit(generate_error_message(sanitized_arguments))

    mapping_dictionary = init_mapping_dictionary()

    parsed_old_format_file = parse_input_file(sanitized_arguments[0])
    new_format = convert_old_to_new_format(mapping_dictionary, parsed_old_format_file)

    if os.path.exists('%s/%s' % (os.getcwd(), sanitized_arguments[1])):
        os.remove('%s/%s' % (os.getcwd(), sanitized_arguments[1]))
    #
    new_format_values = prepare_input_for_csv(new_format)
    write_output(new_format_values, sanitized_arguments[1])


if __name__ == "__main__":
    main()
