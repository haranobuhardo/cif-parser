# boilerplate

from ast import keyword
import pandas as pd
import io, sys
from pathlib import Path
import os
import csv

# set default settings
user_src_folder_path = r'src'
user_dest_folder_path = r'dest'
# file_path = 'qmof-000dce3.cif' # file name and location
loop_seq = 2 # loop number that you want to alter or change
user_column_to_keep = ['_atom_site_type_symbol', '_atom_site_label', 
                        '_atom_site_symmetry_multiplicity',
                        '_atom_site_fract_x',
                        '_atom_site_fract_y',
                        '_atom_site_fract_z'] # edit this to suit your needs
user_keyword_to_find = 'charge'
file_list = []
extend_dest = True # export each result to its own folder

# file_path = sys.argv[1] if len(sys.argv) > 1 else file_path
# loop_seq = sys.argv[2] if len(sys.argv) > 2 else loop_seq

if not(os.path.isdir(user_src_folder_path) or os.path.isdir(user_dest_folder_path)): 
    raise Exception('Source or dest folder not found!')

for file in os.listdir(user_src_folder_path):
    if file.endswith(".cif"):
        file_list.append(file)

# parsing file to python var

def parse_cif(src_folder_path, file_path):
    column_to_keep = user_column_to_keep
    keyword_to_find = user_keyword_to_find

    print('Start parsing', file_path, '...\n')
    with open(os.path.join(src_folder_path, file_path)) as f:
        block_name=''
        columns=[]
        unedited_lines=''
        tables=[]
        loop_cnt = 0

        line = f.readline().strip()
        block_name = line

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
                
def modify_column(column, table, column_to_keep, keyword_to_find):
    column_to_keep = user_column_to_keep
    keyword_to_find = user_keyword_to_find

    # create DataFrame from selected loop_
    df = pd.read_csv(io.StringIO(table.replace('  ', ';')), names=column, sep=';')
    print('Creating table based on extracted data COMPLETED!')

    # filtering and modifying DataFrame
    base_df = df[column_to_keep]
    list_output_df = []
    print('Filtering table\'s column COMPLETED')

    # iterating through all columns, find columns with KEYWORD string in it
    for i in df.columns:
        if keyword_to_find in i:
            _ = base_df.copy()
            _[i] = df[i]
            list_output_df.append(_)
    print('Iterating through column that contain certain text COMPLETED!')

    return list_output_df


if __name__ == "__main__":
    metal_names = {} # for additional feature 08/07/22

    for i_file, file_path in enumerate(file_list): # loop through the source folder
        print('\n##### File no:', i_file+1)
        unedited_files, columns, tables = parse_cif(user_src_folder_path, file_path)
        final_file = unedited_files

        # exporting all possible tables
        for i_table in range(len(tables)):
            if i_table == 1:  #change 1 to table that you want to modify (REMEMBER! index sequencing start from 0 in Python)
                user_list_output_df = modify_column(columns[i_table], tables[i_table], user_column_to_keep, user_keyword_to_find)
            else:
                user_list_output_df = pd.read_csv(io.StringIO(tables[i_table].replace('  ', ';')), names=columns[i_table], sep=';')
                user_list_output_df = user_list_output_df.drop(columns='_symmetry_equiv_pos_site_id')
                unedited_files = unedited_files + \
                            'loop_\n' + '\n'.join(user_list_output_df.columns) + '\n' + \
                            user_list_output_df.to_csv(index=False, header=False, line_terminator='\n', sep='|').replace('|', '  ').replace('"','')
                continue
            
            metal_names[Path(file_path).stem] = user_list_output_df[0]['_atom_site_type_symbol'].values[0] # for additional feature 08/07/22, make sure the metal located on the first column of _atom_site_type_symbol

            for n, i in enumerate(user_list_output_df):
                
                # renaming column that have been found by KEYWORD
                for column in i.columns:
                    if user_keyword_to_find in column:
                        print(column)
                        i = i.rename(columns={column:'_atom_site_charge'})
                        
                final_file = unedited_files + \
                            'loop_\n' + '\n'.join(i.columns) + '\n' + \
                            i.to_csv(index=False, header=False, line_terminator='\n', sep='|').replace('|', '  ').replace('"','')

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
                        'metal_name': metal_names.values()}).to_excel(os.path.join(user_dest_folder_path,'metal_names.xlsx'))