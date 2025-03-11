# No Such Thing As A Free Lunch: Explanation and Review

## Usage
Extract all zipped CSVs to "ELSI_DATA" folder. Run dashboard.py with Python3 and necessary packages (below)

## Data Source

All data for this project was sourced from the [Elementary and Secondary Information System: Table Generator](https://nces.ed.gov/ccd/elsi/tableGenerator.aspx), from the US Department of Education's National Center for Education Statistics (NCES). The data was exported using five seperate custom table exports; the columns used for these visualizations are:

- Free Lunch Eligible
- Reduced-price Lunch Eligible Students
- Direct Certification
- Latitude
- Longitude
- National School Lunch Program
- School ID (12-digit) - NCES Assigned
- School Name
- Total Students, All Grades (Excludes AE)
- Black or African American Students
- White Students
- American Indian/Alaska Native Students
- Asian or Asian/Pacific Islander Students
- Hispanic Students
- Nat. Hawaiian or Other Pacific Isl. Students

Information about the data reporting, errors, and column descriptions as reported by NCES can be found in the Glossary.pdf.

## The Visualization: Goal

ScatterGeo: The goal of this visualization was to show the impact that free lunch potentially has on students across the country. Millions upon millions of students, across a variety of states in a variety of living situations, rely upon the federal government for food during the school day. Many schools report over half their student population eligible. This data visualization hopes to show the breadth and importance of these programs.

BarPie: The goal of this visualization was to display the distributed impact these programs have across racial categories. The pie chart shows the overall percentages, whereas the bar char shows the distribution of these percentages across the same bins as the ScatterGeo. The juxtaposition of the distribution, compared to the totals of the pie chart, hopes to highlight the inequity of the impact of these programs.

As the creation and dismantling of federal education programs are treated as whim, it is important to consider the very real, specific, food-in-the-belly impacts of these sweeping actions.

## The Visualization: Process

What follows is a roughly step-by-step guide to understanding how this data visualization was created. Each step number refers to a specific step marked in the dashboard.py file.

### Imports

The following packages are needed to run this visualization:

- numpy
- pandas
- matplotlib
- seaborn
- os
- plotly
- dash

### Data Cleaning

1. The raw exports from ELSI are read into the program as five different Pandas dataframes. Each row is a unique school; the columns, and their explanations, can be found in the Glossary.pdf.
1. The dataframes are merged on the unique school NCES identifier
1. Copied columns are deleted; data from years not shared across columns are deleted. Certain columns are renamed to make code easier; specific characters are replaced with NAN for DataFrame calculations.
1. From the merged dataframe, the data is split into dataframes correspodning to each year, columns renamed without the year. E.g, merged df had "Latitude (2014-2015)" and "Latitude (2015-2016)". New dataframe "2014" is created that has column "Latitude." These yearly dataframes are stored in a dictionary, with the key as the year.
1. A processing function is defined that converts any numerical column data to floats, and creates new columns that represent calculations performed on other columns. The new columns are:
    - FREE : Total number of FRL Eligible Students, including Direct Certification (some states, like MA, only report DC)
    - RED : Total number of Reduced Lunch Eligible students
    - FREE-RED : The combined total of FREE and RED
    - FLER : ratio of FREE-RED over Total Enrollment; eg, percent of students per school who are Free/Reduced Lunch Eligible
    - FLER-PERC : The FLER ratio as a string that is in percent format, truncated to 2 decimal spaces
    - ETHN_PERC : The ratio of ethnicity population over total population; eg, percent of students of given ethnicity. ETHN is a variable representing ethnicity.
1. These processed dataframes are saved to CSVs within the generated folder "clean_csvs;" each csv is named for the year of data it represents, as in "2014.csv"
1. If the program is run the first time, the processed csvs are generated. After, the program checks to see if the folder clean_csvs is generated. If so, it simply loads those instead. If changes are to be made to the data processing functions, simply delete the clean_csvs folder.
1. An n=10,000 sample is created of the data for the geographical scatterplot. Higher samples result in incredibly slow performance. If no sampling is desired, changing the value of [`df0`] allows full-data visualization.
### Figure 01: ScatterGeo
1. Default values for colors and the legend are set for the ScatterGeo plot. The data is grouped into 10 bins, where each bin represents 10%.
1. A scatterGeo plot is made using Plotly. To avoid creating a plot that simply represents population, the data is all rendered using the calculations for percentages from Step 5.  Each bin is a trace in the plot that can be toggled with the legend; each year is a seperate frame of the plot triggered with a slider animation.  Each school is then colored according to their FLER percentage, and grouped accordingly. Note: although grouped for the legend, the color scale is continous, and thus each school is the color correspdoing to the exact FLER percentage. Each point can be hovered to show the School Name and total FREE-RED count.
1. The layout of the plot is configured for ease of reading and clarity; buttons and sliders are added to toggle frames, as well as "play" or "pause".
1. A single ghost trace was added so as to include a color bar on the right.
1. An HTML of the plot is exported to figure_01.html
### Figure 02: Stacked Bar Chart; Pie Chart
1. A second subplot consisting of a Bar Chart and Pie Chart is made. Each row is assigned a new column "bin", that has an integer representing the bins created in the ScatterGeo.
1. The Pie Charts and Bar Charts are iteratively made, where each frame is a year, and each trace is an ethnicity. The stacked bar chart shows the racial/ethnic percentage of students in relation to the total population, broken down into "bin."
1. The subplots are made to be side by side.
1. The layout for the figures is customized.
1. An HTML of the plot is exported to figure_02.html
### Dash App
1. A Dash Application is launched, with basic seperation of the plots into divs and arranged on the HTML page.

## Issues
### Data
There are some issues in the data visualization; for instance, some states show no schools for certain years. The NCES notes that certain legal provisions may impact the reliability of FRL counts. As copied from the Glossary.pdf on the "Nation School Lunch Program" column:
>>> This variable indicates whether a school participates in the National School Lunch Program, and, if so, under what special provisions. The Healthy, Hunger-Free Kids Act of 2010 (PL 111-296) includes provisions for determining free and reduced-price lunch (FRL) eligibility that may affect the reliability and availability of the FRL counts reported to EDFacts (FS033). Under provisions 2 and 3 of the law, annual certification of individual students is not required. A new provision, the Community Eligibility Option (CEO or Provision 4), eliminates the requirement for individual eligibility information once a school has determined a baseline percentage of FRL eligible students. These changes may result in missing or out of date FRL counts. Education researchers frequently use FRL eligibility as an indicator of student socioeconomic status (SES). The NSLP status provides these researchers with an indication of the reliability of the FRL counts reported in this file.

For the purposes of this visualization, this variable was ignored, and the visualizations were made using the counts. This was chosen because filtering schools with "No" or "NULL" values resulted in more frequent ghost states reporting 0 schools for a few years; as noted by NCES, this can likely be explained by states meeting a minimum threshold percentage and not needing to report.

While the counts for FLE and RED are deemed "non-duplicated," there is still the chance that, through the data calculation, the arrived percentages are not completely accurate due to misreporting or the aforementioned discrepencies in data reporting.

The total ethnic counts for the students do not add up to exactly 100%; this is likely due to students not reporting or missing values for certain schools resulting in these aggregated differences.
### Presentation
The Dash application allows for easy deployability, but the very basic HTML structure leaves much to be desired in terms of aesthetics. For this project, the simple HTML suffices, but is not as pleasing to the eye as could be hoped.
### Intelligibility
The ScatterGeo map is intelligible, but the percentage breakdown can be confusing since it is easy to mistake the map as being that of population.

The Aggregate Ethnic/Racial percentages can be very confusing, particualrly with the bins as the X-Axis. The chart grouped each school into a percentage category (where the percentage is FLER/TOTAL); then stacked percentages of ethnicity (where the percentage is ETHN/TOTAL). This difference in percentage calcualtions, and the fact that everything is a ratio, can be difficult to grasp, even if the chart seems simple to look at.

## Further Steps
With infinite time and resources, this data could be used to make other interesting plots. For instance, within these dataframes, there is additional categorical data on gender breakdown (male/female), school type (elementary, middle, high) and school virtual status (full virtual, partial virtual, non virtual). All of this data was initially intended to be plotted, so as to provide a myriad of subplots to supplement the central scatterGro plot; due to time constraints, only the scatterGeo and the racial subplots were created.

Additionally, further data from other sources could be pulled to add a layer of analysis. For instance, pulling election data could show the difference in these FLER percentages by political affiliation. Hopefully this documentation is sufficient such that anyone who wanted to make those additions, could.
