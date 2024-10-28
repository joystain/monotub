from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

#sql server info nohup python3 mush.py & disown
SERVER = '192.168.0.10'
DATABASE = 'DB1'
USERNAME = 'joy_desk'
PASSWORD = 'Lecrea1!'
PORT = 3306

engine = create_engine(f'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}')
sql = "SELECT * FROM mushdata;"
averages = [[30,50],[800], [72]]


def grab_all_sensor_data():
    #conn = pyodbc.connect(connectionString)
    data = pd.read_sql(sql, engine)
    engine.dispose()
    return data


df = grab_all_sensor_data()
keys = df.keys()[2:5]

df2 = df[['time','humidity','co2','temperature']]
df2.time = df.time.dt.components.hours
df2 = df2.groupby('time').mean().reset_index()


def date_graph():
    for key,avg in zip(keys,averages):
        plt.figure(figsize=[10,4])
        plt.scatter(df.date.iloc[:,[0,2,3,4]])
        plt.title(f"average {key} by date")
        plt.xlabel('Date')
        plt.ylabel(f"{key}")
        for i in avg:
            plt.axhline(y=i, color='r')
        
def time_graph():
    for key,avg in zip(df.keys()[2:5],averages):
        plt.figure(figsize=[10,4])
        plt.plot(df2.time, df2.groupby('time').mean()[key])
        plt.title(f"average {key} by time")
        plt.xlabel('Time')
        plt.ylabel(f"{key}")
        for i in avg:
            plt.axhline(y=i, color='r')
            
def last_day_avg():
    last_day_df = df[df.date == df.date.iloc[-1]].iloc[:,[1,2,3,4]]
    last_day_df.time = last_day_df.time.dt.components.hours
    return last_day_df.groupby('time').mean()





