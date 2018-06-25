from ..data_array import DataSetMixin


class DataSet(DataSetMixin):

    def _write_data(self, data, count, offset):
        dataset = self._h5group.get_dataset("data")
        dataset.write_data(data, count, offset)

    def _read_data(self, data, count, offset):
        dataset = self._h5group.get_dataset("data")
        dataset.read_data(data, count, offset)

    @property
    def data_extent(self):
        """
        The size of the data.

        :type: set of int
        """
        dataset = self._h5group.get_dataset("data")
        return dataset.shape

    @data_extent.setter
    def data_extent(self, extent):
        dataset = self._h5group.get_dataset("data")
        dataset.shape = extent

    @property
    def data_type(self):
        """
        The data type of the data stored in the DataArray. This is a read only
        property.

        :type: DataType
        """
        return self._get_dtype()

    def _get_dtype(self):
        dataset = self._h5group.get_dataset("data")
        return dataset.dtype
