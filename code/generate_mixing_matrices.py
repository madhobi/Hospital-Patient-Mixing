import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bokeh.models import Slider, HoverTool, Select, CustomJS, ColumnDataSource

from data_preparation_for_mixing_matrices import *
from plot_specification_mixing_matrices_normalized import *

def process_data(contact_table_filename, antibiotic_profile_filename):

    # Reading contact information
    contact_table = pd.read_csv(contact_table_filename, delimiter=',', na_values=['\\N'])
    print('Reading contact_table:')
    print(contact_table.head(5))
    print(contact_table.shape)
    data_contact = contact_table.copy()
    # dropping null and duplicate rows
    data_contact.dropna(axis=0,inplace=True)
    data_contact.drop_duplicates(inplace=True)
    print('contact table data shape after drop na and duplicate: ', data_contact.shape)

    # Reading antibiotic exposure information
    print('Reading antibiotic_profile:')
    data_antibiotic_profile_daywise = pd.read_csv(antibiotic_profile_filename, delimiter=',')
    print(data_antibiotic_profile_daywise.head(5))
    print(data_antibiotic_profile_daywise.shape)
    data_antibiotic = data_antibiotic_profile_daywise.copy()

    # dropping null and duplicate rows
    data_antibiotic.dropna(axis=0,inplace=True)
    data_antibiotic.drop_duplicates(inplace=True)
    #print(data_antibiotic.columns)
    print('antibiotic profile shape after drop na and duplicate: ', data_antibiotic.shape)


    data_groupby_hospital = data_contact.groupby('hospitalid')
    unit_list_per_hospital = data_groupby_hospital.apply(lambda x: x['nhsnunitname'].unique())
    unit_list_per_hospital = unit_list_per_hospital.to_dict()
    #updated_hospital_dict = {str(key): value for key, value in unit_list_per_hospital.items()}
    #unit_list_per_hospital = updated_hospital_dict
    #for key, value in updated_hospital_dict.items():
    #    print(key, ' : ', value)

    return data_contact, unit_list_per_hospital, data_antibiotic


def prepare_mixing_matrices(data_contact, unit_list_per_hospital, data_antibiotic):
    # our variables of interest are age, antibiotic_category and elixhauser score
    df_age_matrix = prepare_age_matrix_data(unit_list_per_hospital, data_contact)
    df_elix_score_mixing_matrix = prepare_elixhauser_score_matrix_data(unit_list_per_hospital, data_contact)
    df_antibiotic_mixing = prepare_antibiotic_rank_matrix_data_daywise(data_contact, data_antibiotic, unit_list_per_hospital)


def plot_and_manage_javascript_calling(data_age_mixing, data_elix_score_mixing, data_antibiotic_rank_mixing, data_no_antibiotic_ratio, hospitals_list, unit_list_per_hospital):

    hm_age, source_age_matrix, source_all_age_matrix = plot_hm_age_matrix(data_age_mixing)
    hm_elix_score_normalized, source_elix_score_matrix, source_all_elix_score_matrix = plot_elixhauser_score_matrix_data(data_elix_score_mixing)
    hm_antibiotic_rank, source_antibiotic_mixing_matrix, source_all_antibiotic_mixing_matrix = plot_antibiotic_mixing(data_antibiotic_rank_mixing)
    pie_chart, source_pie_chart, source_all_pie_chart = plot_no_antibiotic_ratio_pie_chart(data_no_antibiotic_ratio)

    # dropdown menu for selecting hospitalid
    dropdown_hospitalid = Select(options=hospitals_list, value='1001', title='Select Hospital')
    # dropdown menu for selecting unit within the selected hospital
    updated_hospital_dict = {str(key): value for key, value in unit_list_per_hospital.items()}
    dropdown_unit_names = Select(options=list(updated_hospital_dict['1001']),value='', title = 'Select Unit')

    sc_unit_list = ColumnDataSource(data=updated_hospital_dict)
    callback_dropdown_hospitalid = CustomJS(
    args=dict(  dd_unit_name=dropdown_unit_names,
                sc_unit_list=sc_unit_list,
                sc=source_age_matrix,
                sc_all=source_all_age_matrix,
                sc_elix_mixing=source_elix_score_matrix,
                sc_all_elix_mixing=source_all_elix_score_matrix,
                sc_antibiotic_mixing_matrix=source_antibiotic_mixing_matrix,
                sc_all_antibiotic_mixing_matrix=source_all_antibiotic_mixing_matrix,
                sc_pie_chart = source_pie_chart,
                sc_all_pie_chart = source_all_pie_chart,
                hm_age_matrix=hm_age,
                hm_elix_score_matrix=hm_elix_score_normalized,
                hm_antibiotic_rank_matrix=hm_antibiotic_rank,
                pie_chart = pie_chart), code="""
    var hid = cb_obj.value
    console.log(hid)
    var hid_dict = sc_unit_list.data
    var unit_list = hid_dict[hid];
    console.log(unit_list);
    dd_unit_name.options = unit_list
    dd_unit_name.value = unit_list[0];
    //console.log(dd_icu_name.value)
    console.log(unit_list[0])

    var unit = dd_unit_name.value
    var data_age = sc_all.data
    var colname_contact_count = hid+ '_' + unit + '_contact_count'
    var colname_normalized_contact_count = hid+ '_' + unit + '_normalized_contact_count'
    var colname_age_x = hid+ '_' + unit + '_age_x'
    var colname_age_y = hid+ '_' + unit + '_age_y'
    sc.data['contact_count'] = data_age[colname_contact_count]
    sc.data['normalized_contact_count'] = data_age[colname_normalized_contact_count]
    sc.data['age_x'] = data_age[colname_age_x]
    sc.data['age_y'] = data_age[colname_age_y]
    sc.change.emit();

    var data_elix = sc_all_elix_mixing.data
    var colname_normalized_contact_count = hid+ '_' + unit + '_normalized_contact_count'
    var colname_elix_x = hid+ '_' + unit + '_ElixhauserScore_x'
    var colname_elix_y = hid+ '_' + unit + '_ElixhauserScore_y'
    sc_elix_mixing.data['normalized_contact_count'] = data_elix[colname_normalized_contact_count]
    sc_elix_mixing.data['ElixhauserScore_x'] = data_elix[colname_elix_x]
    sc_elix_mixing.data['ElixhauserScore_y'] = data_elix[colname_elix_y]
    sc_elix_mixing.change.emit();

    var data_antibiotic = sc_all_antibiotic_mixing_matrix.data
    var colname_freq = hid+ '_' + unit + '_freq'
    var colname_normalized_freq = hid+ '_' + unit + '_normalized_freq'
    var colname_rank_x = hid+ '_' + unit + '_rank_x'
    var colname_rank_y = hid+ '_' + unit + '_rank_y'
    sc_antibiotic_mixing_matrix.data['freq'] = data_antibiotic[colname_freq]
    sc_antibiotic_mixing_matrix.data['normalized_freq'] = data_antibiotic[colname_normalized_freq]
    sc_antibiotic_mixing_matrix.data['rank_x'] = data_antibiotic[colname_rank_x]
    sc_antibiotic_mixing_matrix.data['rank_y'] = data_antibiotic[colname_rank_y]
    sc_antibiotic_mixing_matrix.change.emit();

    var data_no_antibiotic = sc_all_pie_chart.data
    var colname_value = hid+ '_' + unit + 'value'
    var colname_percentage = hid+ '_' + unit + 'percentage'        
    sc_pie_chart.data['value'] = data_no_antibiotic[colname_value]
    sc_pie_chart.data['percentage'] = data_no_antibiotic[colname_percentage]
    var angle = data_no_antibiotic[colname_percentage].slice()    
    for(var i=0; i<angle.length; i++) {
        angle[i] *= 2 * Math.PI;
    }
    sc_pie_chart.data['angle'] = angle
    sc_pie_chart.data['type'] = data_no_antibiotic['type']
    sc_pie_chart.data['color'] = data_no_antibiotic['color']    
    console.log(colname_percentage)
    console.log(sc_pie_chart.data['percentage'])
    //console.log(Math.PI)     
    //console.log(sc_pie_chart.data['angle'])    
    sc_pie_chart.change.emit();


    //hm_age_matrix.title.text = "Mixing Matrix by Age on " + unit + "(" + hid + ")"
    //hm_elix_score_matrix.title.text = "Mixing Matrix by Elixhauser Score on " + unit + "(" + hid + ")"
    //hm_antibiotic_rank_matrix.title.text = "Mixing Matrix by Antibiotic Spectrum on " + unit + "(" + hid + ")"

    hm_age_matrix.title.text = "Mixing Matrix by Age"
    hm_elix_score_matrix.title.text = "Mixing Matrix by Elixhauser Score"
    hm_antibiotic_rank_matrix.title.text = "Mixing Matrix by Antibiotic Spectrum"
    pie_chart.title.text = "Pie chart of antibiotic exposure"

    """)

    dropdown_hospitalid.js_on_change('value', callback_dropdown_hospitalid) # calling the function on change of selection


    callback_dropdown_unit_names = CustomJS(
    args=dict(  dd_hid=dropdown_hospitalid,
                sc=source_age_matrix,
                sc_all=source_all_age_matrix,
                sc_elix_mixing=source_elix_score_matrix,
                sc_all_elix_mixing=source_all_elix_score_matrix,
                sc_antibiotic_mixing_matrix=source_antibiotic_mixing_matrix,
                sc_all_antibiotic_mixing_matrix=source_all_antibiotic_mixing_matrix,
                sc_pie_chart = source_pie_chart,
                sc_all_pie_chart = source_all_pie_chart,
                hm_age_matrix=hm_age,
                hm_elix_score_matrix=hm_elix_score_normalized,
                hm_antibiotic_rank_matrix=hm_antibiotic_rank,
                pie_chart = pie_chart), code="""
    var unit = cb_obj.value
    var hid = dd_hid.value
    console.log(hid)
    console.log(unit)
    var data_age = sc_all.data
    var colname_contact_count = hid+ '_' + unit + '_contact_count'
    var colname_normalized_contact_count = hid+ '_' + unit + '_normalized_contact_count'
    var colname_age_x = hid+ '_' + unit + '_age_x'
    var colname_age_y = hid+ '_' + unit + '_age_y'
    sc.data['contact_count'] = data_age[colname_contact_count]
    sc.data['normalized_contact_count'] = data_age[colname_normalized_contact_count]
    sc.data['age_x'] = data_age[colname_age_x]
    sc.data['age_y'] = data_age[colname_age_y]
    sc.change.emit();

    var data_elix = sc_all_elix_mixing.data
    var colname_normalized_contact_count = hid+ '_' + unit + '_normalized_contact_count'
    var colname_elix_x = hid+ '_' + unit + '_ElixhauserScore_x'
    var colname_elix_y = hid+ '_' + unit + '_ElixhauserScore_y'
    sc_elix_mixing.data['normalized_contact_count'] = data_elix[colname_normalized_contact_count]
    sc_elix_mixing.data['ElixhauserScore_x'] = data_elix[colname_elix_x]
    sc_elix_mixing.data['ElixhauserScore_y'] = data_elix[colname_elix_y]
    sc_elix_mixing.change.emit();

    var data_antibiotic = sc_all_antibiotic_mixing_matrix.data
    var colname_freq = hid+ '_' + unit + '_freq'
    var colname_normalized_freq = hid+ '_' + unit + '_normalized_freq'
    var colname_rank_x = hid+ '_' + unit + '_rank_x'
    var colname_rank_y = hid+ '_' + unit + '_rank_y'
    sc_antibiotic_mixing_matrix.data['freq'] = data_antibiotic[colname_freq]
    sc_antibiotic_mixing_matrix.data['normalized_freq'] = data_antibiotic[colname_normalized_freq]
    sc_antibiotic_mixing_matrix.data['rank_x'] = data_antibiotic[colname_rank_x]
    sc_antibiotic_mixing_matrix.data['rank_y'] = data_antibiotic[colname_rank_y]
    sc_antibiotic_mixing_matrix.change.emit();

    var data_no_antibiotic = sc_all_pie_chart.data
    var colname_value = hid+ '_' + unit + 'value'
    var colname_percentage = hid+ '_' + unit + 'percentage'        
    sc_pie_chart.data['value'] = data_no_antibiotic[colname_value]
    sc_pie_chart.data['percentage'] = data_no_antibiotic[colname_percentage]
    var angle = data_no_antibiotic[colname_percentage].slice()    
    for(var i=0; i<angle.length; i++) {
        angle[i] *= 2 * Math.PI;
    }
    sc_pie_chart.data['angle'] = angle
    sc_pie_chart.data['type'] = data_no_antibiotic['type']
    sc_pie_chart.data['color'] = data_no_antibiotic['color']
    console.log(colname_percentage)
    console.log(sc_pie_chart.data['percentage'])
    //console.log(Math.PI)     
    //console.log(sc_pie_chart.data['angle'])    
    sc_pie_chart.change.emit();

    //hm_age_matrix.title.text = "Mixing Matrix by Age on " + unit + "(" + hid + ")"
    //hm_elix_score_matrix.title.text = "Mixing Matrix by Elixhauser Score on " + unit + "(" + hid + ")"
    //hm_antibiotic_rank_matrix.title.text = "Mixing Matrix by Antibiotic Spectrum on " + unit + "(" + hid + ")"

    hm_age_matrix.title.text = "Mixing Matrix by Age"
    hm_elix_score_matrix.title.text = "Mixing Matrix by Elixhauser Score"
    hm_antibiotic_rank_matrix.title.text = "Mixing Matrix by Antibiotic Spectrum"
    pie_chart.title.text = "Pie chart of antibiotic exposure"

    """)



    #dropdown_icu_names = Select(options=list(icu_names),value='Medical Cardiac Critical Care', title = 'Select Unit')  # drop down menu
    dropdown_unit_names.js_on_change('value', callback_dropdown_unit_names) # calling the function on change of selection

    ############### code for dropdown ends ################


    #layout = column(row(dropdown_hospitalid, dropdown_unit_names),
    #            row(hm_age, hm_elix_score_normalized, hm_antibiotic_rank), pie_chart)
    layout = column(row(dropdown_hospitalid, dropdown_unit_names),
        row(hm_age, hm_elix_score_normalized),
        row(hm_antibiotic_rank, pie_chart))

    return layout
    #show(layout)
