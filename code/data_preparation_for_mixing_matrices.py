import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def prepare_age_matrix_data(unit_list_per_hospital, data):

	print('Creating age matrix dataframe..')
	df_age_mixing = pd.DataFrame()
	age_possible_values = data.age.unique()
	age_possible_values.sort()
	#print('Possible values of age: ', age_possible_values)
	age_value_count = len(age_possible_values)
    # initializing the dataframe with highest number of possible rows
	df_age_mixing['Age'] = list(age_possible_values) * age_value_count
	print(df_age_mixing.head(5))
	print(df_age_mixing.shape)
	scale_min, scale_max = 0, 1
	unit_counter=1
	for key, value in unit_list_per_hospital.items(): # key : hospitalid and value: corresponding icu_list
		#print(key, ' : ', value)
		for unit_name in value:
			data_subset = data[(data['hospitalid'] == key) &
							(data['nhsnunitname'] == unit_name)]
			#print(data_subset)
			print('Data size in hospital: ', key, ', unit: ', unit_name)
			print(data_subset.shape)
			unit_counter += 1
			data_subset = data_subset[['contactid','patientid', 'admissionid', 'age']].copy()

			data_merged = pd.merge(data_subset, data_subset, on='contactid')
			#print('merged data shape: ', data_merged.shape)
			data_contact = data_merged[data_merged['patientid_x'] != data_merged['patientid_y']]

			df = data_contact.groupby(['age_x', 'age_y']).size().reset_index(name='contact_count')
			col_min, col_max = df.contact_count.min(), df.contact_count.max()
			if(col_max == col_min):
				col_max = col_min + 1
			df['normalized_contact_count'] = (df.contact_count - col_min) / (col_max - col_min) * (scale_max - scale_min) + scale_min
			x_colname = str(key)+'_'+unit_name+'_age_x'
			y_colname = str(key)+'_'+unit_name+'_age_y'
			count_colname = str(key)+'_'+unit_name+'_contact_count'
			normalized_count_colname = str(key)+'_'+unit_name+'_normalized_contact_count'
			df_age_mixing[x_colname] = df['age_x']
			df_age_mixing[y_colname] = df['age_y']
			df_age_mixing[count_colname] = df['contact_count']
			df_age_mixing[normalized_count_colname] = df['normalized_contact_count']


	print('df_age_matrix: ')
	print(df_age_mixing.head(5))
	print('df_age_mixing shape: ', df_age_mixing.shape)
	print('total hospital unit number: ', unit_counter)
	df_age_mixing.to_csv('../data/age_mixing_hospital_unitwise.csv', index=False)
	return df_age_mixing

def prepare_elixhauser_score_matrix_data(unit_list_per_hospital, data):

	print('Creating ElixhauserScore dataframe..')
	df_elix_score_mixing = pd.DataFrame()
	elix_score_possible_values = data.ElixhauserScore.unique()
	elix_score_value_count = len(elix_score_possible_values)
	elix_score_possible_values.sort()
    # initializing the dataframe with highest number of possible rows
	df_elix_score_mixing['ElixhauserScore'] = list(elix_score_possible_values) * elix_score_value_count

	scale_min, scale_max = 0, 1
	for key, value in unit_list_per_hospital.items(): # key : hospitalid and value: corresponding icu_list
		#print(key, ' : ', value)
		for unit_name in value:
			#data_subset = data_contact[(data_contact['hospitalid'] == key) &
			#                            (data_contact['nhsnunitname'] == unit_name)]
			data_subset = data[(data['hospitalid'] == key) &
							(data['nhsnunitname'] == unit_name)]
			data_subset = data_subset[['contactid','patientid', 'admissionid', 'ElixhauserScore']].copy()
			print('Data size in hospital: ', key, ', unit: ', unit_name)
			print(data_subset.shape)

			data_merged = pd.merge(data_subset, data_subset, on='contactid')
			#print('merged data shape: ', data_merged.shape)
			data_contact = data_merged[data_merged['patientid_x'] != data_merged['patientid_y']]
			#print(data_contact.head(10))
			#print('contact data shape: ', data_contact.shape)

			df = data_contact.groupby(['ElixhauserScore_x', 'ElixhauserScore_y']).size().reset_index(name='contact_count')
			col_min, col_max = df.contact_count.min(), df.contact_count.max()
			if(col_max == col_min):
				col_max = col_min + 1
			df['normalized_contact_count'] = (df.contact_count - col_min) / (col_max - col_min) * (scale_max - scale_min) + scale_min
			x_colname = str(key)+'_'+unit_name+'_ElixhauserScore_x'
			y_colname = str(key)+'_'+unit_name+'_ElixhauserScore_y'
			count_colname = str(key)+'_'+unit_name+'_contact_count'
			normalized_count_colname = str(key)+'_'+unit_name+'_normalized_contact_count'
			df_elix_score_mixing[x_colname] = df['ElixhauserScore_x']
			df_elix_score_mixing[y_colname] = df['ElixhauserScore_y']
			df_elix_score_mixing[count_colname] = df['contact_count']
			df_elix_score_mixing[normalized_count_colname] = df['normalized_contact_count']

	print('df_elix_score_mixing shape: ', df_elix_score_mixing.shape)
	#print(df_elix_score_mixing.columns)
	df_elix_score_mixing.to_csv('../data/elix_score_mixing_hospital_unitwise.csv', index=False)

	return df_elix_score_mixing

def prepare_antibiotic_rank_matrix_data_daywise(data, data_antibiotic_profile_daywise, unit_list_per_hospital):

	print("Preparing antibiotic mixing matrices..")
	data_antibiotic_profile_subset = data_antibiotic_profile_daywise[['hospitalid', 'patientid', 'admissionid', 'administrationdate','a', 'b', 'c', 'd']]
	print(data_antibiotic_profile_subset.head(10))
	print(data_antibiotic_profile_subset.shape)
	#pandas.merge(df1, df2, how='left', left_on=['id_key'], right_on=['fk_key'])
	#data_icu_patient_with_antibiotic_profile = pd.merge(data_icu, data_antibiotic_profile_subset, on=['hospitalid', 'patientid', 'admissionid'])
	data_patient_with_antibiotic_profile = pd.merge(data, data_antibiotic_profile_subset, how='left',
	    left_on=['hospitalid', 'patientid', 'admissionid', 'day_of_contact'],
	    right_on=['hospitalid', 'patientid', 'admissionid', 'administrationdate'])
	print(data_patient_with_antibiotic_profile.head(5))
	print('data_patient_with_antibiotic_profile shape: ', data_patient_with_antibiotic_profile.shape)
	data_patient_with_antibiotic_profile.dropna(axis=0,inplace=True)
	print('data_patient_with_antibiotic_profile shape after dropping na: ', data_patient_with_antibiotic_profile.shape)
	print(data_patient_with_antibiotic_profile.columns)
    #exit(1)

	key_column_list = ['contactid','hospitalid','nhsnunitid', 'nhsnunitname','day_of_contact' ]
	scale_min, scale_max = 0, 1
	df_antibiotic_rank_freq = pd.DataFrame()
	cols = ['a_x', 'b_x', 'c_x', 'd_x']
	inds = ['a_y', 'b_y', 'c_y', 'd_y']
	for key, value in unit_list_per_hospital.items(): # key : hospitalid and value: corresponding unit_list
	    for unit_name in value:
	        print(str(key),': ', unit_name)
	        data_subset = data_patient_with_antibiotic_profile[(data_patient_with_antibiotic_profile['hospitalid'] == key) &
	                                    (data_patient_with_antibiotic_profile['nhsnunitname'] == unit_name)]
	        data_subset = data_subset[['contactid','patientid', 'a', 'b', 'c', 'd']].copy()
	        print('data_subset shape: ', data_subset.shape)
	        data_merged = pd.merge(data_subset, data_subset, on='contactid')
	        print('merged data shape: ', data_merged.shape)
	        data_antibiotic_contact = data_merged.copy()
	        data_antibiotic_contact = data_merged[data_merged['patientid_x'] != data_merged['patientid_y']]
	        #print(data_contact.head(10))
	        #print(data_contact.shape)
	        x = []
	        y = []
	        freq = []
	        for col in cols:
	            for ind in inds:
	                df = data_antibiotic_contact[(data_antibiotic_contact[col] >= 1) & (data_antibiotic_contact[ind] >= 1)]
	                #print(col, ',', ind)
	                #print(len(df))
	                x.append(col[0]) # taking only the first character to remove '_x' from the label
	                y.append(ind[0])
	                if(len(df) == 0):
	                	freq.append(np.nan)
	                else:
	                	freq.append(len(df))

	        x_colname = str(key)+'_'+unit_name+'_rank_x'
	        y_colname = str(key)+'_'+unit_name+'_rank_y'
	        count_colname = str(key)+'_'+unit_name+'_freq'
	        normalized_count_colname = str(key)+'_'+unit_name+'_normalized_freq'
	        df_antibiotic_rank_freq[x_colname] = x
	        df_antibiotic_rank_freq[y_colname] = y
	        df_antibiotic_rank_freq[count_colname] = freq
	        col_min, col_max = df_antibiotic_rank_freq[count_colname].min(), df_antibiotic_rank_freq[count_colname].max()
	        if(col_max == col_min):
	            col_max = col_min + 1
	        df_antibiotic_rank_freq[normalized_count_colname] = (df_antibiotic_rank_freq[count_colname] - col_min) / (col_max - col_min) * (scale_max - scale_min) + scale_min

	print(df_antibiotic_rank_freq.head(5))
	print(df_antibiotic_rank_freq.shape)
	df_antibiotic_rank_freq.to_csv('../data/antibiotic_rank_mixing_hospital_unitwise_with_nan.csv', index=False)
	return df_antibiotic_rank_freq
