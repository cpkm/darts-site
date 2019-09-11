import pandas as pd

# The schedule needs the following format
# Date, Team, Location, Playoff
# 01/02/2019, 'Real Deal 2', 'H', 'n'
# 08/02/2019, 'Fat Duck 2', 'A', 'n'

debug = 0

#This allows playoffs to be set as y/n, p/r or 1/0
class DartSchedule:
    def __init__(self):
        self.df_    = pd.DataFrame()

    def FormatColumnNames(self):
        #Makes sure the title names are what is expected
        self.df_.columns = self.df_.columns.str.title().str.strip(' ')
        return self.df_

    @staticmethod
    def StripAndMap(column: pd.Series, mapping: dict) -> pd.Series:
        column = column.str.lower()
        column = column.str.strip(' ')
        column = column.str.strip("'")
        column = column.str.strip('"')
        column = column.map(mapping)
        return column

    @staticmethod
    def FormatDate(dates):
        return dates

    @staticmethod
    def FormatTeam(teams):
        teams = teams.str.title()
        return teams

    @staticmethod
    def FormatLocation(locations):
        mapping = {'h': True, 'a': False, 'icc': True}
        if locations.dtype != 'bool':
            locations = DartSchedule.StripAndMap(locations,mapping)
            if debug:
                print('After FormatLocation...')
                print(locations.head())
            locations = locations.astype('bool')
        return locations

    @staticmethod
    def FormatPlayoff(playoffs):
        #Turns loose playoff formatting into a boolean column
        mapping = { 'y': True, 'n': False, 'r' : False, 'p' : True }
        if playoffs.dtype != 'bool':
            playoffs = DartSchedule.StripAndMap(playoffs,mapping)
            if debug:
                print('After FormatPlayoff...')
                print(playoffs.head())
            playoffs = playoffs.astype('bool')
        return playoffs

    def FormatEntries(self):
        self.df_.Date = DartSchedule.FormatDate(self.df_.Date)
        self.df_.Team = DartSchedule.FormatTeam(self.df_.Team)
        self.df_.Location = DartSchedule.FormatLocation(self.df_.Location)
        self.df_.Playoff = DartSchedule.FormatPlayoff(self.df_.Playoff)
        return self.df_

    def CheckColumns(self):
        #Checks that all of the columns that are needed exist
        needed_columns = ['Date', 'Team', 'Location', 'Playoff']
        missing_lst = [ missing for missing in needed_columns if missing not in self.df_.columns ]
        if len(missing_lst) > 0:
            raise ValueError('Missing columns: {}'.format(missing_lst))

    def read_csv(self,filename):
        #Reads the schedule from a csv
        self.df_ = pd.read_csv(filename)
        if debug:
            print('After Reading...')
            print(self.df_.head())
        self.FormatColumnNames()
        if debug:
            print('After FormatColumnNames...')
            print(self.df_.head())
        self.CheckColumns()
        self.FormatEntries()
        if debug:
            print('After FormatEntries...')
            print(self.df_.head())
        return self.df_

