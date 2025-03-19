def add_shock_events(df):
    df['shock_event'] = 'None'

    df.loc[(df['Date'] >= '2018-02-01') & (df['Date'] <= '2018-03-31'), 'shock_event'] = 'volmageddon'
    df.loc[(df['Date'] >= '2020-02-15') & (df['Date'] <= '2020-05-01'), 'shock_event'] = 'covid_crash'
    df.loc[(df['Date'] >= '2022-06-01') & (df['Date'] <= '2022-12-31'), 'shock_event'] = 'fed_hike_inflation'

    return df
