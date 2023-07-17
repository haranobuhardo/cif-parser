# boilerplate

# from ast import keyword
# import csv
# import re
import pandas as pd
import io, sys
from pathlib import Path
import os

# set default settings
user_src_folder_path = r'src'
user_dest_folder_path = r'dest'
loop_table_no = 2 # loop number that you want to alter or change
user_column_to_keep = [ # edit this to suit your needs
                        # '_atom_site_type_symbol', 
                        '_atom_site_label', 
                        # '_atom_site_symmetry_multiplicity',
                        '_atom_site_fract_x',
                        '_atom_site_fract_y',
                        '_atom_site_fract_z'
                    ] 
metal_name_column = '_atom_site_label'
user_keywords_to_find = ['charge']
target_keyword_column_name = '_atom_site_charge'
file_list = []
extend_dest = True # export each result to its own folder

if not(os.path.isdir(user_src_folder_path) or os.path.isdir(user_dest_folder_path)): 
    raise Exception('Source or dest folder not found!')

for file in os.listdir(user_src_folder_path):
    if file.endswith(".cif"):
        file_list.append(file)

file_list.sort() # sort file list

# parsing file to python var

def parse_cif(src_folder_path, file_path):
    column_to_keep = user_column_to_keep
    keywords_to_find = user_keywords_to_find

    print('Start parsing', file_path, '...\n')
    with open(os.path.join(src_folder_path, file_path)) as f:
        block_name=''
        columns=[]
        unedited_lines=''
        tables=[]
        loop_cnt = 0
        block_name_keyword = 'data_'

        while block_name == '':
            line = f.readline().strip()
            unedited_lines += line + '\n'
            block_name = line if line.startswith(block_name_keyword) else ''

        while line:
            if(line.strip() == 'loop_'):
                loop_cnt += 1
                # unedited_lines += line + '\n'
                line = f.readline().strip()
                
                # if loop_cnt == selected_loop_no:
                # parse columns
                go_on = True
                while go_on:
                    columns.append(list())
                    columns[loop_cnt-1].append(line)
                    line = f.readline().strip()
                    if line[0] != '_': go_on = False
                            
                # parse columns' values
                go_on = True
                tables.append('')
                while go_on and line:
                    tables[loop_cnt-1] += line + '\n'
                    line = f.readline().strip()
                    if line == 'loop_': 
                        go_on = False
                        # unedited_lines += line + '\n'
            else:
                unedited_lines += line + '\n'
                line = f.readline().strip()
    print('Finding the selected loop COMPLETED!')
    print('\tBlock name:', block_name)
    print('\tNumber of loops inside this data:', loop_cnt)

    return unedited_lines, columns, tables
                
def modify_column(column, table, column_to_keep, keywords_to_find):
    column_to_keep = user_column_to_keep
    keywords_to_find = user_keywords_to_find

    # create DataFrame from selected loop_
    # _table_virtual_file = io.StringIO(';'.join(re.split('''\s+(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', table)))
    df = pd.read_csv(io.StringIO(table), names=column, sep='\s+')
    print('Creating table based on extracted data COMPLETED!')

    # filtering and modifying DataFrame
    base_df = df[column_to_keep]
    list_output_df = []
    print('Filtering table\'s column COMPLETED')


    # iterating through all columns, find columns with KEYWORD string in it
    for i in df.columns:
        if any(keyword in i for keyword in keywords_to_find):
            _ = base_df.copy()
            _[i] = df[i]
            list_output_df.append(_)

    # if no keyword found on any columns, just output the default table with column to keep
    if len(list_output_df) == 0:
        list_output_df.append(base_df)

    print('Iterating through column that contain certain text COMPLETED!')

    return list_output_df


def main():
    metal_names = {} # for additional feature 08/07/22

    for i_file, file_path in enumerate(file_list): # loop through the source folder
        print('\n##### File no:', i_file+1)
        unedited_lines, columns, tables = parse_cif(user_src_folder_path, file_path)
        final_file = unedited_lines

        # exporting all possible tables
        for i_table in range(len(tables)):
            if i_table == loop_table_no-1:
                user_list_output_df = modify_column(columns[i_table], tables[i_table], user_column_to_keep, user_keywords_to_find)
            else:
                # table_virtual_file = io.StringIO(';'.join(re.split('''\s+(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', tables[i_table])))
                user_list_output_df = pd.read_csv(io.StringIO(tables[i_table]), names=columns[i_table], sep='\s+')
                unedited_lines = unedited_lines + \
                            'loop_\n' + '\n'.join(user_list_output_df.columns) + '\n' + \
                            user_list_output_df.to_csv(index=False, header=False, lineterminator='\n', sep='|').replace('|', '  ').replace('"','')
                continue
                
            metal_names[Path(file_path).stem] = user_list_output_df[0][metal_name_column].values[0] # for additional feature 08/07/22, make sure the metal located on the first column of _atom_site_type_symbol

            for n, i in enumerate(user_list_output_df):
                
                # renaming column that have been found by KEYWORD - toggle by initial setting
                for column in i.columns:
                    if any(keyword in column for keyword in user_keywords_to_find):
                        print(column)
                        i = i.rename(columns={column:target_keyword_column_name})
                        
                final_file = unedited_lines + \
                            'loop_\n' + '\n'.join(i.columns) + '\n' + \
                            i.to_csv(index=False, header=False, lineterminator='\n', sep='|').replace('|', '  ').replace('"','')

                # check folder availability
                extended_dest_folder = str(n) if extend_dest else ''
                dest_folder = os.path.join(user_dest_folder_path, extended_dest_folder)
                is_dest_folder_exist = os.path.exists(dest_folder)
                if not is_dest_folder_exist: os.makedirs(dest_folder)

                _target_file = os.path.join(dest_folder, Path(file_path).stem + '_' + str(n) + '.cif')
                with open(_target_file, 'w') as f:
                    f.write(final_file)
                    print('Export', _target_file, 'COMPLETED!\n')
    
     # for additional feature 08/07/22
    print(pd.DataFrame({'file_name': metal_names.keys(), 
                        'metal_name': metal_names.values()}))
    
    pd.DataFrame({'file_name': metal_names.keys(), 
                        'metal_name': metal_names.values()}).to_csv(os.path.join(user_dest_folder_path,'metal_names.csv'))

if __name__ == "__main__":
    main()