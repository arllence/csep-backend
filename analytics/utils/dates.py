from datetime import datetime


class DateClass:
    '''
    Contains utility functions to convert dates to other date time formats
    '''

    def __init__(self):
        pass

    def convertto_datetime(self, input_date):
        # formatted_date = datetime.strptime(input_date, "%m/%d/%Y %I:%M %p")
        # formatted_date = datetime.strptime(input_date, "%d-%b-%Y-%H:%M:%S")
        formatted_date = input_date
        return formatted_date

    def compare_dates(self, start_date, end_date):
        if start_date < end_date:
            return True
        elif start_date == end_date:
            return True
        else:
            return False
