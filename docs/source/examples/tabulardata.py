import nixio
import numpy as np
from collections import OrderedDict


def main():
    nixfile = nixio.File.open("dataframe.nix", nixio.FileMode.Overwrite)
    block = nixfile.create_block("test block", "recordingsession")
    column_definitions = OrderedDict([('name', str), ('id', str), ('time', float),
                                      ('amplitude', np.float64), ('frequency', np.float64)])

    column_units = ["", "", "s", "mV", "Hz"]
    column_data = [("alpha", nixio.util.create_id()[:10], 20.18, 5.0, 100),
                   ("beta", nixio.util.create_id()[:10], 20.09, 5.5, 101),
                   ("gamma", nixio.util.create_id()[:10], 20.05, 5.1, 100),
                   ("delta", nixio.util.create_id()[:10], 20.15, 5.3, 150),
                   ("epsilon", nixio.util.create_id()[:10], 20.23, 5.7, 200),
                   ("fi", nixio.util.create_id()[:10], 20.07, 5.2, 300),
                   ("zeta", nixio.util.create_id()[:10], 20.12, 5.1, 39),
                   ("eta", nixio.util.create_id()[:10], 20.27, 5.1, 600),
                   ("theta", nixio.util.create_id()[:10], 20.15, 5.6, 400),
                   ("iota", nixio.util.create_id()[:10], 20.08, 5.1, 200)]

    data_frame = block.create_data_frame("test data frame", "signal1",
                                         data=column_data, col_dict=column_definitions)
    data_frame.units = column_units

    data_frame.print_table()

    print("size, aka number of rows: ", data_frame.size)
    print("column names: ", data_frame.column_names)
    print("column definition: ", data_frame.columns)
    print("column units: ", data_frame.units)

    print("single cell by position: ", data_frame.read_cell(position=(0, 0)))
    print("single cell by name and row index: ", data_frame.read_cell(col_name="name", row_idx=[0]))

    print("Entire ID column: ", data_frame.read_columns(name="id"))
    print("Two columns, id and name, joined: ", data_frame.read_columns(name=["id", "name"]))

    print("Entire rows with indices 0 and 2: ", data_frame.read_rows([0, 2]))

    nixfile.close()


if __name__ == "__main__":
    main()
