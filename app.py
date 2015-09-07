from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import pandas as pd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index')
def index():
    return render_template('form.html', message = "")

def get_data(start_year, end_year, animal):
	# Loading the dataset on scientific procedures on animals in the UK
    data = requests.get('https://www.quandl.com/api/v3/datasets/GUARDIAN/ANIMAL_TESTING.json?auth_token=APubRyAz2zP5ZWsNhDs2')
    parsed_data = json.loads(data.text)
    # Making it a pandas DataFrame
    df = pd.DataFrame(parsed_data)
    # Converting the dates into timestamps
    for i in df['dataset']['data']:
    	i[0] = pd.to_datetime(i[0])
    # Keeping only the data
    plotting_data = df['dataset'][2:4]
    # Making a Bokeh-licious plot
    # First selecting the data
    years = []
    numbers = []
    index_of_animal = plotting_data['column_names'].index(animal)
    for i in plotting_data['data']:
    	i_year = i[0].year
    	if (i_year >= start_year and i_year <= end_year):
    	    years.append(i_year)
    	    numbers.append(i[index_of_animal])
    return [years, numbers]

def make_plot(years, numbers, animal, start_year, end_year):
	# The Data is ready for the plot
	if animal == "Total":
		animal = "All animals"
	f = figure(height = 700, width = 1200, title = "Scientific Procedures on " + str(animal) + " Between " + str(start_year) + " and " + str(end_year) + " in the UK")
	f.line(years, numbers, color='#1F78B4')
	f.xaxis.axis_label = "Year"
	f.yaxis.axis_label = "Number of Scientific Procedures"
	div,script = components(f, CDN)
	return [div, script]

@app.route('/getting_form', methods=['POST', 'GET'])
def getting_form():
	# Getting the data from the form
    start_year = int(request.form['Start_Year'])
    end_year = int(request.form['End_Year'])
    if end_year <= start_year:
    	return render_template('form.html', message = "Please select an end year posterior to the start year.")
    animal = request.form['Animal_Type']
    if animal == "All":
    	animal = "Total"
    years, numbers = get_data(start_year, end_year, animal)    
    div, script = make_plot(years, numbers, animal, start_year, end_year)
    return render_template('plot.html', div = div, script = script)

if __name__ == '__main__':
	app.run(port=33507, debug=True)