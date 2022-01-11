import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.transform import cumsum
#from bokeh.models.widgets import Panel, Tabs
from bokeh.io import export_png
#output_file('antibiotic_rank_mixing.html')

plot_width_global = 510
plot_height_global = 510


def generate_source_pie_chart(data_pie_chart, hid, unit_name):

	data_pie_chart['color'] = ['blue', 'orange', 'yellow']
	#source_all_pie_chart = ColumnDataSource(data_pie_chart)
	source_pie_chart = ColumnDataSource(
		data = dict(
			type = data_pie_chart['type'],
			value = data_pie_chart[str(hid)+'_'+unit_name+'value'],
			percentage = data_pie_chart[str(hid)+'_'+unit_name+'percentage'],
			angle = data_pie_chart[str(hid)+'_'+unit_name+'percentage'] * 2 * pi,
			color = data_pie_chart['color']
			#color = Category10[len(data_no_antibiotic_ratio)]
		)
	)
	return source_pie_chart



def generate_pie_chart(source_pie_chart, hid, unit_name):   

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    pie_chart = figure(title=""+unit_name+" ("+str(hid)+")", plot_width=plot_width_global,
            plot_height=plot_height_global, tools=TOOLS,
            tooltips="@type: @percentage%")

    pie_chart.wedge(x=1, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='type', source=source_pie_chart)
    pie_chart.legend.label_text_font_size = "15pt"
    pie_chart.title.text_font_size = '15pt'

    return pie_chart


def main():
	print('Hello there! We will generate the mixing matrices by antibiotic ranks in loop and save them as png \N{grinning face}')
    
	
	data = pd.read_csv('../../data/contact_table_all_patient.csv', delimiter=',', na_values=['\\N'])
	data.dropna(axis=0,inplace=True)
	data.drop_duplicates(inplace=True)
	print('data shape after dropping null and duplicate: ', data.shape)

	#data_antibiotic_profile_daywise = pd.read_csv('../data/daywise_count_profile.csv', delimiter=',')
	#print(data_antibiotic_profile_daywise.head(5))
	#print(data_antibiotic_profile_daywise.shape)

	data_groupby_hospital = data.groupby('hospitalid')
	unit_list_per_hospital = data_groupby_hospital.apply(lambda x: x['nhsnunitname'].unique())
	unit_list_per_hospital = unit_list_per_hospital.to_dict()

	#data_age_mixing = pd.read_csv('age_mixing_hospital_unitwise.csv', delimiter=',')
	#print(data_age_mixing.head(5))
	#print(data_age_mixing.columns)
	#data_elix_score_mixing = pd.read_csv('elix_score_mixing_hospital_unitwise.csv', delimiter=',')
    
	data_pie_chart = pd.read_csv('../data/antibiotic_exposed_vs_no_antibiotic_proportion.csv', delimiter=',')
	#data_pie_chart = data_antibiotic_rank_mixing.drop(24)
	print(data_pie_chart.columns)
	print(data_pie_chart.shape)
	print(data_pie_chart.head(5))
	#exit(1)
	
	counter = 1
	for hid, unit_list in unit_list_per_hospital.items(): # key : hospitalid and value: corresponding unit_list
		for unit_name in unit_list:
			print(str(hid),': ', unit_name)
			
			#source_age_matrix = generate_source_age_matrix(data_age_mixing, hid, unit_name)
			#source_elix_score_matrix = generate_source_elix_score_matrix(data_elix_score_mixing, hid, unit_name)
			source_pie_chart = generate_source_pie_chart(data_pie_chart, hid, unit_name)

			#hm_age = generate_hm_age(source_age_matrix, hid, unit_name)
			#hm_elix_score_normalized = generate_hm_elixhauser_score(source_elix_score_matrix, hid, unit_name)
			pie_chart = generate_pie_chart(source_pie_chart, hid, unit_name)

			#hm_age_filename = str(hid)+'_'+unit_name+'_age_matrix.png'
			unit_name_concatenated = unit_name.replace(' ', '_').replace('/', '_')
			#hm_age_filename = "./plots/normalized/age_matrix/"+unit_name_concatenated+'_'+str(hid)+'_age_matrix.png'
			#hm_elix_score_filename = "./plots/normalized/elix_score_matrix/"+unit_name_concatenated+'_'+str(hid)+'_elix_score_matrix.png'
			#hm_antibiotic_rank_filename = "./plots/normalized/antibiotic_rank_matrix_with_no_antibiotic/"+unit_name_concatenated+'_'+str(hid)+'_antibiotic_rank_matrix.png'
			pie_chart_filename = "../../dason_mixing_matrices/plots/normalized/pie_chart/font_15/"+unit_name_concatenated+'_'+str(hid)+'.png'
			#export_png(hm_age, filename=hm_age_filename)
			#export_png(hm_elix_score_normalized, filename=hm_elix_score_filename)
			export_png(pie_chart, filename=pie_chart_filename)
			#print(hm_age_filename)
			#print(hm_elix_score_filename)
			print(pie_chart_filename)
			#export_png(hm_age, filename="./plots/plot"+str(counter)+".png")			
			counter += 1
    
    #print("total unit count: ", str(counter))



if __name__ == "__main__":
    main()