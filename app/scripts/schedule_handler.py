import pandas as pd

# The schedule needs the following format
# Date, Team, Location, Playoff
# 01/02/2019, 'Real Deal 2', 'H', 'n'
# 08/02/2019, 'Fat Duck 2', 'A', 'n'

#This allows playoffs to be set as y/n, p/r or 1/0
DEBUG = 1

def FormatColumnNames(df):
    #Makes sure the title names are what is expected
    df.columns = df.columns.str.title().str.strip(' ')
    return df

def FormatDate(dates):
    return dates

def FormatTeam(teams):
    teams = teams.str.title()
    return teams

def FormatLocation(locations):
    return locations

def FormatPlayoff(playoffs):
    #Turns loose playoff formatting into a boolean column
    mapping = { 'y': True, 'n': False, 'r' : False, 'p' : True }
    if playoffs.dtype != 'bool':
        playoffs = playoffs.str.lower()
        playoffs = playoffs.str.strip(' ')
        playoffs = playoffs.str.strip("'")
        playoffs = playoffs.str.strip('"')
        if DEBUG:
            print('After FormatPlayoff...')
            print(playoffs.head())
        playoffs = playoffs.map(mapping)
        playoffs = playoffs.astype('bool')
        if DEBUG:
            print('After mapping...')
            print(playoffs.head())
    return playoffs

def FormatEntries(df):
    df.Date = FormatDate(df.Date)
    df.Team = FormatTeam(df.Team)
    df.Location = FormatLocation(df.Location)
    df.Playoff = FormatPlayoff(df.Playoff)
    return df

def CheckColumns(df):
    #Checks that all of the columns that are needed exist
    needed_columns = ['Date', 'Team', 'Location', 'Playoff']
    missing_lst = [ missing for missing in needed_columns if missing not in df.columns ]
    if len(missing_lst) > 0:
        raise ValueError('Missing columns: {}'.format(missing_lst))

def read_csv(filename):
    #Reads the schedule from a csv
    df_sched = pd.read_csv(filename)
    if DEBUG:
        print('After Reading...')
        print(df_sched.head())
    df_sched = FormatColumnNames(df_sched)
    if DEBUG:
        print('After FormatColumnNames...')
        print(df_sched.head())
    CheckColumns(df_sched)
    df_sched = FormatEntries(df_sched)
    if DEBUG:
        print('After FormatEntries...')
        print(df_sched.head())
    return df_sched

