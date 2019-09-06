import tabula
import pandas as pd

def StackClean(df):
    df['Week'] = df.iloc[0, 1]
    df.columns = ['Away Team','at','Home Team','Date','Week']
    df.reset_index(inplace=True,drop=True)
    df.drop(0,inplace=True)
    df.Date = pd.to_datetime(df.Date)
    return df

def SplitRow(df):
    df.reset_index(inplace=True,drop=True)
    left_date = df.iloc[0,3].split(' ')[0]
    right_date = df.iloc[0,6]

    left_df = df.iloc[:,:3]
    left_df['Date'] = left_date
    right_df = df.iloc[:,3:6]
    right_df['Date'] = right_date

    left_df = StackClean(left_df)
    right_df = StackClean(right_df)

    return left_df.append(right_df)

def readpdftab(filename):
    pd.set_option('mode.chained_assignment', None)
    df = tabula.read_pdf(filename, mulitple_tables=True,guess=False,pages='all')
    return df

def tidy(df):
    #Find rows where 'Week' is present
    row_headers = list(df[df.iloc[:,1].str.contains('Week').fillna(False)].index.values)
    row_headers.append(len(df))    #Do the last slice
    row_list = []
    for row_idx in range(0,len(row_headers)-1):
        row_list.append(df.iloc[row_headers[row_idx]:row_headers[row_idx+1],:])

    df_tidy = pd.DataFrame()
    for row in row_list:
        df_tidy = df_tidy.append(SplitRow(row))
    return df_tidy

def map_names(df):
    mapping = {'Fat Duck 1' : 'Fat Duck',
               'Italian-Canadian' : 'ICC',
               'Shakespeare' : "Shakey's",
               'Penny Whistle' : 'Pennywhistle',
               'Woolwich Arms' : 'Wooly'}
    df['Home Team'] = df['Home Team'].replace(mapping,regex=True)
    df['Away Team'] = df['Away Team'].replace(mapping,regex=True)
    return df

def convert_to_game(row):
    date = row['Date']
    week = row['Week']
    if(row['Home Team'] == 'ICC 4'):
        opponent = row['Away Team']
        home = True
    else:
        opponent = row['Home Team']
        home = False

    return DartMatch(opponent,home,date,week)

class DartSchedulePDF:
    def __init__(self,file_loc):
        df_raw = readpdftab(file_loc)
        df_tidy = tidy(df_raw)
        df_mapped = map_names(df_tidy)
        df_icc4 = df_mapped[(df_mapped['Home Team'] == 'ICC 4') | (df_mapped['Away Team'] == 'ICC 4')]
        df_icc4.sort_values('Date', inplace=True)
        self.game_list_  = [convert_to_game(row) for index, row in df_icc4.iterrows()]

    def get_game(self,idx):
        return self.game_list_[idx]

class DartMatch:
    def __init__(self,opponent, home, date, week):
        self.opponent   = opponent
        self.home       = home
        self.date       = date
        self.week       = week




