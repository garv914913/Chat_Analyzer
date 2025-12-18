import re
import pandas as pd
from datetime import datetime

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-\s'

    message = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': message, 'message_date': dates})
    #convert message data type
    df['message_date'] = pd.to_datetime(df['message_date']
        .str.replace('\u202f', ' ', regex=False)  # replace narrow non-breaking space
        .str.replace('\u00a0', ' ', regex=False),  # replace normal non-breaking space
        format='%m/%d/%y, %H:%M %p - ')

    df.rename(columns = {'message_date': 'date'}, inplace = True)

    #Seperate Users and Messages
    users = []
    messages = []
    for message in df['user_message']:
        if not isinstance(message, str):
            message = str(message)
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['users'] = users
    df['messages'] = messages
    df.drop(columns=['user_message'], inplace=True)


    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['only_d'] = df['date'].dt.date
    df['only_date'] = pd.to_datetime(df['only_d'])
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['hour_label'] = df['date'].dt.strftime('%I %p')
    df['minute'] = df['date'].dt.minute

    period = []
    for (hour_label, hour) in zip(df['hour_label'], df['hour']):
        if hour_label == '11 PM':
            period.append(str(hour_label) + "-" + str('00 AM'))
        elif hour_label == '11 AM':
            period.append(str(hour_label) + "-" + str('12 PM'))
        elif hour_label == '12 PM':
            period.append(str(hour_label) + "-" + str('1 PM'))
        elif hour_label == '00 AM':
            period.append(str(hour_label) + "-" + str('1 AM'))
        else:
            start = hour_label
            end = datetime.strptime(str((hour + 1) % 24), "%H").strftime("%I %p")
            period.append(f"{start}-{end}")

    df['period']= period

    return df
