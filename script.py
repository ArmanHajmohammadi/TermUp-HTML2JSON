import json
from bs4 import BeautifulSoup
import re


def process_schedule(input_string):
    # Find all parts beginning with "درس"
    parts = re.findall(r'درس\(.*?\): .*?(?=\s*درس|\s*$)', input_string)

    # Remove the "درس(*): " words from each part
    cleaned_parts = [re.sub(r'درس\(.*?\): ', '', part) for part in parts]

    return cleaned_parts


def convert_schedule(input_array):
    days_mapping = {
        "شنبه": 0,
        "یک شنبه": 1,
        "دوشنبه": 2,
        "سه شنبه": 3,
        "چهارشنبه": 4,
        "پنج شنبه": 5,
        "جمعه": 6
    }

    output_array = []

    for schedule in input_array:
        print(schedule)
        parts = schedule.split()
        if 'ف' in parts:
            parts.remove('ف')
        if 'ز' in parts:
            parts.remove('ز')
        if 'نیمه2' in parts:
            parts.remove('نیمه2')
        if 'ت' in parts:
            parts.remove('ت')
        day = " ".join(parts[:-1])  # Combine day parts
        time_range = parts[-1].split('-')

        start_time = time_range[0].split(':')
        end_time = time_range[1].split(':')

        start_hour = int(start_time[0])
        start_minute = int(start_time[1])

        end_hour = int(end_time[0])
        end_minute = int(end_time[1])

        day_index = days_mapping.get(day)

        if day_index is not None:
            start_decimal = start_hour + start_minute / 60
            end_decimal = end_hour + end_minute / 60

            output_array.append([day, [start_decimal, end_decimal]])

    return output_array


def remove_exam_info(input_string):
    # Remove the part after "امتحان" and the word "امتحان"
    exam_index = input_string.find("امتحان")
    if exam_index != -1:
        input_string = input_string[:exam_index]
    input_string = input_string.replace("امتحان", "")

    # Remove the phrase "حل تمرین(ت)" and replace it with "درس(ت)"
    input_string = input_string.replace("حل تمرین(ت):", "درس(ت):")

    return input_string


def replace_arabic_chars(text):
    # Replace "ك" with "ک"
    text = text.replace("ك", "ک")

    # Replace "ي" with "ی"
    text = text.replace("ي", "ی")

    return text


# Read the HTML document
with open('data.txt', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <td> tags with the specified np-col-name attributes
td_tags = soup.find_all('td', {
                        'np-col-name': ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11"]})

# Initialize an empty list to store the extracted data
data = []

# Iterate through the <td> tags and extract data
for i in range(0, len(td_tags), 11):
    code = replace_arabic_chars(td_tags[i].text)
    title = replace_arabic_chars(td_tags[i + 1].text)
    total = replace_arabic_chars(td_tags[i + 2].text)
    useless = replace_arabic_chars(td_tags[i + 3].text)
    capacity = replace_arabic_chars(td_tags[i + 4].text)
    gender = replace_arabic_chars(td_tags[i + 5].text)
    professor = replace_arabic_chars(td_tags[i + 6].text)
    classes = process_schedule(remove_exam_info(
        replace_arabic_chars(td_tags[i + 7].text)))
    location = replace_arabic_chars(td_tags[i + 8].text)
    classDays = convert_schedule(classes)
    # Create a dictionary for each row
    row_data = {
        'code': code,
        'title': title,
        'total': total,
        'useless': useless,
        'capacity': capacity,
        'gender': gender,
        'professor': professor,
        'location': location,
        'classes': classes,
        "classDays": classDays
    }

    # Append the row data to the list
    data.append(row_data)

# Save the data as a JSON file
with open('output.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print("Data extracted and saved to 'output.json'")
