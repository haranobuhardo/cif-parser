import numpy as np
import os

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_mol_file(mol_filename):
    """ Reads a .mol file and extracts atomic data. """
    atoms = []
    with open(mol_filename, 'r') as file:
        lines = file.readlines()
    
    # Find the start of atomic coordinates (skip the first few header lines)
    start_index = 2  # Assuming first few lines are headers
    while not lines[start_index].strip()[0].isdigit():  
        start_index += 1  # Find the first line with numerical values
    
    for line in lines[start_index:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        atom_label = parts[4] + parts[0]  # Example: C1, O2
        x, y, z = map(float, parts[1:4])
        atoms.append((atom_label, parts[4], x, y, z))

    return atoms

def cartesian_to_fractional(cart_coords, lattice_vectors):
    """ Converts Cartesian coordinates to fractional coordinates. """
    lattice_matrix = np.array(lattice_vectors)
    inv_lattice_matrix = np.linalg.inv(lattice_matrix)
    
    cart_matrix = np.array(cart_coords).T  # Convert to a matrix
    fractional_coords = inv_lattice_matrix @ cart_matrix  # Matrix multiplication
    return fractional_coords.T  # Transpose back

def write_cif_file(cif_filename, atoms, lattice_vectors):
    """ Writes atomic data into a .cif file. """
    with open(cif_filename, 'w') as file:
        file.write("_citation_year       2010\n")
        file.write(f"_cell_length_a       {lattice_vectors[0][0]:.3f}\n")
        file.write(f"_cell_length_b       {lattice_vectors[1][1]:.3f}\n")
        file.write(f"_cell_length_c       {lattice_vectors[2][2]:.3f}\n")
        file.write(f"_cell_angle_alpha    90\n")
        file.write(f"_cell_angle_beta     90\n")
        file.write(f"_cell_angle_gamma    90\n")
        file.write(f"_cell_volume         {np.linalg.det(lattice_vectors):.0f}\n")
        file.write("\n_symmetry_cell_setting    triclinic\n")
        file.write("_symmetry_space_group_name_Hall 'P 1'\n")
        file.write("_symmetry_space_group_name_H-M 'P 1'\n")
        file.write("_symmetry_Int_Tables_number 1\n")
        file.write("_symmetry_equiv_pos_as_xyz 'x,y,z'\n\n")
        file.write("loop_\n")
        file.write("_atom_site_label\n")
        file.write("_atom_site_type_symbol\n")
        file.write("_atom_site_fract_x\n")
        file.write("_atom_site_fract_y\n")
        file.write("_atom_site_fract_z\n")
        file.write("_atom_site_charge\n")
        
        # Convert Cartesian to Fractional coordinates
        cartesian_coords = [(x, y, z) for _, _, x, y, z in atoms]
        fractional_coords = cartesian_to_fractional(cartesian_coords, lattice_vectors)
        
        for i, (atom_label, atom_type, _, _, _) in enumerate(atoms):
            fx, fy, fz = fractional_coords[i]
            file.write(f"{atom_label}  {atom_type}  {fx:.5f}  {fy:.5f}  {fz:.5f}  0\n")

# Configuration: Update these lattice vectors based on your material's properties
LATTICE_VECTORS = [
    [59.872, 0, 0],
    [0, 59.872, 0],
    [0, 0, 59.872]
]

def mol_to_cif(mol_filename, cif_filename, lattice_vectors):
    """ Converts a .mol file to a .cif file. """
    atoms = read_mol_file(mol_filename)
    write_cif_file(cif_filename, atoms, lattice_vectors)
    print(f"Conversion successful: {mol_filename} → {cif_filename}")

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Convert .mol file to .cif file.")
    parser.add_argument("input", help="Path to the source .mol file")
    parser.add_argument("output", help="Path to the destination .cif file")

    args = parser.parse_args()

    mol_to_cif(args.input, args.output, LATTICE_VECTORS)
