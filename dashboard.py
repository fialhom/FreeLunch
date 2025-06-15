##########      IMPORTS     ##########

print("NO SUCH THING AS A FREE LUNCH\n\n")
print('Importing packages ...', end=" ", flush=True)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
from dash import dcc, html
print('done.')

##########      DATA CLEANING     ##########
def init_clean():
    ##  01  ##  --  Read in CSVs
    print('Loading CSVs ...',  end=" ", flush=True)
    df1 = pd.read_csv('ELSI_DATA/ELSI_01.csv')
    df2 = pd.read_csv('ELSI_DATA/ELSI_02.csv')
    df3 = pd.read_csv('ELSI_DATA/ELSI_03.csv')
    df4 = pd.read_csv('ELSI_DATA/ELSI_04.csv')
    df5 = pd.read_csv('ELSI_DATA/ELSI_05.csv')
    print('done.')

    ##  02  ##  --  Merge DFs
    print('Merging Data ...',  end=" ", flush=True)
    df5.drop(columns=['School Name', 'State Name [Public School] Latest available year'], inplace=True)
    dfa = pd.merge(df1, df2, on="School ID (12-digit) - NCES Assigned [Public School] Latest available year")
    dfb = pd.merge(df3, df4, on="School ID (12-digit) - NCES Assigned [Public School] Latest available year")
    dfd = pd.merge(dfa, dfb, on="School ID (12-digit) - NCES Assigned [Public School] Latest available year")
    dfc = pd.merge(dfd, df5, on="School ID (12-digit) - NCES Assigned [Public School] Latest available year")

    ##  03  ##  --  Remove cols, Rename, Convert to NA
    del_suff = ["_y_x", "_x_y", "_y_y"]
    for col in dfc.columns:
        if col[-4:] in del_suff: 
            dfc.drop(columns=col, inplace=True) 
        if col[-4:] == "_x_x":
            dfc.rename(columns={col:col[:-4]}, inplace=True) 
        if col[-7:] == "2012-13":
            dfc.drop(columns=col, inplace=True)

    dfc.rename(columns={"School ID (12-digit) - NCES Assigned [Public School] Latest available year": "NCES_ID", "State Name [Public School] Latest available year":"State Name"}, inplace=True)
    dfc.replace(["–", "?", "†", "‡"], np.nan, inplace=True)
    print('done.')
    
    ##  04  ##  --  Create new DF per year; rename cols
    print('Processing dataframes ...',  end=" ", flush=True)
    dfs_old = {}
    dfs = {}
    years = {'2023':[], '2022':[], '2021':[], '2020':[], '2019':[], '2018':[], '2017':[], '2016':[], '2015':[], '2014':[], '2013':[]}

    for col in dfc.columns:
        if col[-7:-3] in years:
            for year in years:
                if col[-7:-3] == year:
                    years[year].append(col)

    for year in years:
        cols = ["School Name", "State Name", "NCES_ID"]
        for col in years[year]:
            cols.append(col)
        df_name = f"{year}"
        dfs_old[df_name] = dfc[cols]

    for df_it in dfs_old:
        df = dfs_old[df_it]
        cols = {}
        for col in df.columns:
            split = col.split('[')
            cols[col] = split[0].strip()
        df_copy = df.copy()
        df_copy.rename(columns=cols, inplace=True)
        dfs[df_it] = df_copy

    ## 05 ##    --  Create function to calculate new columns; create dict of processed DFs
    ethn = ["White Students", "Black or African American Students","American Indian/Alaska Native Students", "Asian or Asian/Pacific Islander Students", "Hispanic Students", "Nat. Hawaiian or Other Pacific Isl. Students"]

    def proc(df00):
        df0 = df00.copy()
        non_int = ['School Name', 'State Name', 'NCES_ID', 'National School Lunch Program', 'School Level (SY 2017-18 onward)', 'Virtual School Status (SY 2016-17 onward)', 'School Type', 'Agency Type', 'Title I School Status', 'School Level', 'Virtual School Status']

        for col in df0.columns:
            if col in non_int:
                continue
            else:
                df0[col] = df0[col].astype(float)

        def update_column_free(row):
            if pd.isna(row['Free Lunch Eligible']):
                try:
                    return row['Direct Certification']
                except KeyError:
                    return 0
            else:
                return row['Free Lunch Eligible']
            
        def update_column_red(row):
            if pd.isna(row['Reduced-price Lunch Eligible Students']):
                return 0
            else:
                return row['Reduced-price Lunch Eligible Students']
        def update_column_red(row):
            if pd.isna(row['Reduced-price Lunch Eligible Students']):
                return 0
            else:
                return row['Reduced-price Lunch Eligible Students']

        df0['FREE'] = df0.apply(update_column_free, axis=1)
        df0['RED'] = df0.apply(update_column_red, axis=1)
        df0['FREE-RED'] = df0['FREE'] + df0['RED']
        df0 = df0[df0['FREE-RED'] != 0]

        df0['FLER'] = df0['FREE-RED'] / df0['Total Students All Grades (Excludes AE)']
   
        dfclean = df0.dropna(subset=['FLER'])
        #dfclean = dfclean[dfclean['National School Lunch Program'] != 'No'] ## Uncomment to filer "No" reporting schools
        dfcleaner = dfclean.copy()
        
        dfcleaner['FLER-PERC'] = dfcleaner['FLER'] * 100
        dfcleaner['FLER-PERC'] = dfcleaner['FLER-PERC'].apply(lambda x: f'{x:.2f}')

        for eth in ethn:
            percent = f'{eth}_PERC'
            dfcleaner[percent] = dfcleaner[eth] / dfcleaner['Total Students All Grades (Excludes AE)'] * 100
        """
        NEW COLUMNS ::
        
        FREE :: total number of FRL Eligible, including Direct Certification (some states, like MA, only report DC)
        RED :: total number of Reduced Lunch Eligible
        FREE-RED :: combined total of FREE and RED
        FLER :: ratio of FREE-RED over Total Enrollment; eg, percent of students on FRL
        FLER-PERC :: the ratio as a string that is in percent format, with 2 decimal spaces
        {ETHN}_PERC :: the ratio of ethnicity population over total population; eg, percent of students of given ethnicity
        
        """
        return dfcleaner

    dfs_clean = {}

    for dfx in dfs:
        df_clean = proc(dfs[dfx])
        dfs_clean[dfx] = df_clean
    print('done.')
    
    ## 06 ##    --  Save all processed csvs to folder for quicker load later
    print('Writing new csvs ...',  end=" ", flush=True)
    for year, df in dfs_clean.items():
        filename = f"clean_csvs/{year}.csv"
        df.to_csv(filename)
    print('done.')

    return dfs_clean

## 07 ##    --  Run Program Init, or Load processed CSVs
try:
    os.mkdir("clean_csvs")
    dfs_clean = init_clean()
except FileExistsError:
    dfs_clean = {}
    print("Loading Processed CSVs ...", end= " ", flush=True)
    for file in os.scandir('clean_csvs'):
        with open(file.path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
            name = f"{file.path}"
            name = name[11:-4]
            dfs_clean[name] = df
    print('done.')

## 08 ##    --  Create a sample of the data, n=10,000, random=314
dfs_clean = dict(sorted(dfs_clean.items()))
dfs_samps = {}
samp_num = 10000
for dfx in dfs_clean:
    df_samp = dfs_clean[dfx].sample(n=samp_num, random_state=314)
    dfs_samps[dfx] = df_samp

dfs0 = dfs_samps 
#dfs0 = dfs_clean # Uncomment to sample entire population

##########      CREATE FIG 01     ##########

## 09 ##    --  Define values and create necessary containers (lists, sets)
limits_10_percent = [(i / 10, (i + 1) / 10) for i in range(10)]  # 0-10%, 10-20%, ..., 90-100%
colortest = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
scl = 'rainbow'
title_template = "Percentage of Students Eligible for Free or Reduced Lunch (Public School)"
frames = []
legend_entries = set()

## 10 ##    --  Create ScatterGeo Figure 01
print('Plotting ScatterGeo ...',  end=" ", flush=True)
fig = go.Figure()

# Make one frame per year
for yearplot, df in dfs0.items():
    totals = "{:,}".format(df['FREE-RED'].sum().astype(int)) # Calculate the total for the current year
    frame_data = []
    show_legend = True if yearplot == '2013' else False
    # Make one trace per limit
    for i, lim in enumerate(limits_10_percent):
        df_sub = df[(df['FLER'] >= lim[0]) & (df['FLER'] < lim[1])]
        trace_name = f"{int(lim[0] * 100)}-{int(lim[1] * 100)}%"
        legend_visible = show_legend and (trace_name not in legend_entries) # set legend visibility to avoid duplicate legend entries
        if legend_visible:
            legend_entries.add(trace_name)

        frame_data.append(go.Scattergeo(
            lat=df_sub['Latitude'],
            lon=df_sub['Longitude'],
            text=df_sub['School Name'] + "<br>" + df_sub['FREE-RED'].astype(int).astype(str)
                + " students<br>" + df_sub['FLER-PERC'].astype(str) + "% of student population",
            hoverinfo='text',
            marker=dict(
                color=df_sub['FLER'] * 100,  
                colorscale=scl,
                cmin=0,
                cmax=100,
                size=6,
                opacity=0.8,
                line_width=0.5,
            ),
            name=trace_name,
            legendgroup=trace_name
    ))
    frames.append(go.Frame(
        data=frame_data,
        name=yearplot,
        layout=go.Layout(
            title={
                'text': f"{title_template}<br> Total Students: {totals}",  # Dynamic title with totals
                'x': 0.5,
                'font': {'size': 28}
            }
        )
    ))

# Initialize with first year data
initial_data = frames[0]['data']
fig.add_traces(initial_data)

## 11 ##    --   Set layout for the figure, sliders, buttons
fig.update_layout(
    title={
        'text': f"{title_template}<br> Total Students: {totals}",
        'x': 0.5,
        'font': {
            'size': 28,
        }
    },
    showlegend=True,
    geo=dict(
        scope='usa',
        showland=True,
        landcolor="rgb(217, 217, 217)",
        projection_type='albers usa',
        showcountries=True,
        showsubunits=True,
        resolution=50,
        lonaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            range=[-140.0, -55.0],
            dtick=5
        ),
        lataxis=dict(
            showgrid=True,
            gridwidth=0.5,
            range=[20.0, 60.0],
            dtick=5
        ),
    ),
    legend=dict(
        title=dict(
            text="Toggle Visible Percent Range",
            font=dict(size=12)
        ),
        font=dict(
            size=12
        ),
        itemsizing='constant',
        itemwidth=30,
        bordercolor="Black",
        borderwidth=1,
        orientation="h",
        y=0.0,
        x=0,
    ),
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {"frame": {"duration": 500, "redraw": True}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Year:',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 500, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0.03,
        'steps': [{'args': [
            [year],
            {'frame': {'duration': 500, 'redraw': True},
             'mode': 'immediate',
             'transition': {'duration': 300}}
        ],
            'label': year[-4:],
            'method': 'animate'} for year in dfs0.keys()]
    }]
)

## 12 ##    --   Adding a visible color bar using an invisible trace; add all traces and frames to fig
colorbar_trace = go.Scattergeo(
    lat=[None], lon=[None],
    mode='markers',
    marker=dict(
        color=colortest,
        colorscale=scl,
        colorbar=dict(
            title=dict(
                text='Percent of Student Population',
                side='right',
            ),
            tickvals=colortest
        ),
    ),
    showlegend=False  # Hide this dummy trace from the legend
)

fig.add_trace(colorbar_trace)
fig.update(frames=frames)
print('done.')

## 13 ##    --  Save to HTML file (optional)
fig.write_html("Figure_01.html", auto_play=False)

##########      CREATE FIG 02     ##########

## 14 ##    --  Define init values and create necessary containers and functions (lists)
def binner(row): # function that adds "bin" column with integer representing bin for bar chart
    for i, lim in enumerate(limits_10_percent):
        if row > lim[0] and (row < lim[1]):
            limstr = str(lim)
            if limstr[6] == "1":
                ls = f"90-100%"
            elif limstr[3] == "0":
                ls = f"0-10%"
            else:
                ls = f"{limstr[3]}0-{limstr[8]}0%"
            return ls
    return 0

ethn = ["White Students", "Black or African American Students", "American Indian/Alaska Native Students", 
        "Asian or Asian/Pacific Islander Students", "Hispanic Students", "Nat. Hawaiian or Other Pacific Isl. Students"]
ethn_perc = [f'{eth}_PERC' for eth in ethn]

frames2 = []
buttons2 = []
traces = []
legend_entries2 = set()
color_scale = px.colors.qualitative.Safe
title_template2 = "Percentage of School Population on Free or Reduced Lunch, by Racial Category"

## 15 ##    --  Create Bar and Pie charts by looping over years
print('Plotting BarChart, PieChart ...',  end=" ", flush=True)
count = 0
for year, df in dfs0.items():
    df['bin'] = df['FLER'].apply(lambda x: binner(x)) # Adds column that represents the "bin" each row is in
    averages = df.groupby('bin')[ethn_perc].mean().reset_index()
    averages = averages[averages['bin'] != 0]
    frame_data = []

    # Create bar chart traces for each ethnicity; add to frame data
    for i, eth_name in enumerate(ethn):
        eth = f'{eth_name}_PERC'
        frame_data.append(go.Bar(
            x=averages['bin'],  
            y=averages[eth], 
            name=eth_name,  
            marker=dict(color=color_scale[i]),
            hovertext=averages[eth].astype(int).astype(str) + "%<br>" + eth_name, 
            hoverinfo='text',
        ))

    # Create pie chart trace for this year; add to frame data
    pie_values = averages[ethn_perc].mean().values
    pie_trace = go.Pie(
        labels=ethn, 
        values=pie_values, 
        marker=dict(colors=color_scale),
        hovertext=ethn,
        showlegend=False,
        hoverinfo='text'
    )
    frame_data.append(pie_trace)

    # Create a frame for this year
    frames2.append(go.Frame(data=frame_data, name=str(year)))

    # Add button for this year
    buttons2.append(dict(
        label=str(year),
        method='animate',
        args=[
            [str(year)],
            {
                'mode': 'immediate',
                'frame': {'duration': 500, 'redraw': True},
                'transition': {'duration': 500}
            }
        ]
    ))
    count+=1

# Add play button to buttons list
play_button = dict(
    label="Play",
    method="animate",
    args=[
        None, 
        {
            'frame': {'duration': 500, 'redraw': True},
            'transition': {'duration': 500},
            'fromcurrent': True,
            'mode': 'immediate'
        }
    ]
)
buttons2.append(play_button)

## 16 ##    --  Make subplots; Initialize with first year of data per frame, trace
fig2 = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "bar"}, {"type": "pie"}]],
    column_widths=[0.7, 0.3]
)

initial_frame = frames2[0].data
for trace in initial_frame:
    fig2.add_trace(trace, row=1, col=1 if isinstance(trace, go.Bar) else 2)
    
## 17 ##    --   Set layout for the figures, dropdowns, buttons
fig2.update_layout(
    title={
        'text': title_template2.format(''),
        'x': 0.5,
        'y': 1,
        'font': {
            'size': 28,
        }
    },
    barmode='stack',
    xaxis_title='Average Percentages of Students on Free-Reduced Lunch',  
    yaxis_title='Percent of Total Population', 
    legend_title='Legend',
    updatemenus=[{
        'buttons': buttons2,
        'direction': 'down',
        'showactive': True,
        'x': 0.0,
        'y': 1.2
    }],
    legend=dict(
        orientation='h',
        xanchor='left',
        yanchor='bottom',
        x=0,
        y=1
    ),
    annotations=[
        dict(
            text="Total Racial Percentage of Students Enrolled <br>at Free-Reduced Lunch Eligible Schools",
            xref="paper", yref="paper",
            x=0.95, y=-0.1,
            showarrow=False
        )
    ]
)
# Update frames with animated data
fig2.update(frames=frames2)
print('done.')

## 18 ##    --  Save to HTML file (optional)
fig2.write_html("Figure_02.html", auto_play=False)

##########      MAKE DASH APP    ##########

## 19 ##    --  Arrange simple HTML layout with Dash
print("Starting Dash...\n")
string=f" To ease load times, data is a sample n={samp_num} schools. For more infomation on missing values or data reporting, please see GLOSSARY.pdf and README.md"
app = dash.Dash(__name__)
app.layout = html.Div(
    # Header, Source
    children=[
        html.H1("No Such Thing As A Free Lunch", style={'textAlign': 'center', 'fontSize': 30}),
        
        html.P(["Data compiled using multi-column exports from ",
            html.A("National Center for Education Statistics (NCES).", href='https://nces.ed.gov/ccd/elsi'),
            string],
            style={'size':'10'}),
        
        # ScatterGeo Div
        html.Div(
            children=[
                html.H2("Individual School Data"),
                dcc.Graph(id='animated-map', figure=fig, style={'height': '90vh', 'width': '100%'})
            ],
            id='content-div'
        ),
        # SubPlot (barchart, piechart) Div
        html.Div(
            children=[
                html.H2("Aggregated Data"),
                dcc.Graph(id='bar_chart', figure=fig2, style={'height': '80vh'})
            ],
            id='content-div-2'
        )
    ]
)
# Run the app
if __name__ == '__main__':
    app.run()
