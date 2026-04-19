# Crystal Structure Toolkit (CIF Parser & MOL Converter)

A simple Crystallographic Information File (CIF) parser built with Python and Pandas. This script extracts specific loops from CIF files, filters columns based on user preferences, and can search for and rename specific columns (e.g., charge-related columns).

## Workflow: The Full Pipeline

This toolkit handles the end-to-end preparation of crystal structures for research:

### Step 1: Convert (MOL → CIF)
If your structure is currently in a `.mol` format (common in **Material Studio**), use the converter in the `mol-to-cif-converter/` folder to generate a base CIF file with fractional coordinates.
```bash
python3 mol-to-cif-converter/convert.py SRC_MOL_FILE_HERE DESTINATION_CIF_FILE_HERE
```
> **Note:** You must manually update the `LATTICE_VECTORS` variable inside `mol-to-cif-converter/convert.py` to match your material's specific dimensions before running the script.

### Step 2: Parse & Clean (CIF → Standardized CIF)
Once you have your CIF files, use the main `parse.py` script to strip unnecessary columns and ensure charge labels are correctly formatted for simulation engines.
```bash
python3 parse.py
```

## Features

- **Format Conversion**: Converts Cartesian coordinates from `.mol` files into Fractional coordinates for `.cif`.
- **Loop Extraction**: Specifically targets and modifies a specified `loop_` block within CIF files.
- **Column Filtering**: Retains a set of predefined columns (`_atom_site_label`, `_atom_site_fract_x`, etc.).
- **Keyword Search**: Identifies and renames columns containing specific keywords (e.g., 'charge').
- **CSV Export**: Generates a summary `metal_names.csv` mapping filenames to the value of a specific column (e.g., the metal name).
- **Flexible Destination**: Can export each result into its own subfolder or a single destination directory.

## Prerequisites

- Python 3.x
- Check libraries on `requirements.txt`

## Installation

1.  Clone this repository or download the `parse.py` script.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The script is configured through variables at the top of `parse.py`:

- `user_src_folder_path`: Directory containing the source `.cif` files (default: `src`).
- `user_dest_folder_path`: Directory where the modified files will be saved (default: `dest`).
- `loop_table_no`: The index of the `loop_` block you wish to modify (default: `2`).
- `user_column_to_keep`: A list of column labels to keep from the selected loop.
- `user_keywords_to_find`: A list of keywords to search for in other columns.
- `target_keyword_column_name`: The new name for any column that matches the keywords.
- `extend_dest`: If `True`, exports each processed variation into a separate subfolder (e.g., `dest/0/`, `dest/1/`).

## Usage

1.  Place your `.cif` files in the source directory (e.g., `src/`).
2.  Adjust the configuration in `parse.py` if necessary.
3.  Run the script:
    ```bash
    python3 parse.py
    ```

The processed files will be available in the destination directory (`dest/`), and a summary `metal_names.csv` will be created.

## Use Cases & Compatibility

This script was originally developed to assist in preparing Crystallographic Information Files for research and thesis work in materials science. It is particularly useful for:

- **Molecular Simulations**: Standardizing CIF files for use in software like **RASPA**, **Zeo++**, or **GCMC** simulations where clean atomic coordinates and specific charge labels (`_atom_site_charge`) are required.
- **Structure Visualization**: Simplifying complex CIFs for easier import into visualization tools like **VESTA** or **Mercury** by removing redundant or incompatible loop data.
- **Data Pre-processing**: Converting raw database exports (e.g., from the CCDC or ICSD) into a consistent format for high-throughput computational screening.

## Example

### Input (src/example.cif)
```cif
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
_atom_site_U_iso_or_equiv
Cu1 Cu 0.2416(7) 1.07587(27) 0.2876(8) 0.0089
O1 O 0.3507(8) 0.99172(28) 0.0651(10) 0.0089
```

### Output (dest/0/example_0.cif)
```cif
loop_
_atom_site_label
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Cu1  0.2416(7)  1.07587(27)  0.2876(8)
O1  0.3507(8)  0.99172(28)  0.0651(10)
```

## How it Works

1.  **Parsing**: The script reads the CIF file line by line to identify `data_` blocks and `loop_` sections.
2.  **Processing**: It uses Pandas to read the table data within the specified loop.
3.  **Modification**: It filters the DataFrame to keep only requested columns and searches for any columns containing the specified keywords.
4.  **Exporting**: It reconstructs the CIF file with the modified table data and saves it to the destination path.

## History

This project was originally created 3 years ago to help a lecturer prepare crystal structure data for their thesis. It has been preserved as a lightweight utility for the materials science community.

