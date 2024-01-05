class ImportUtils:
    def __init__(self, column_headers):
        self.column_headers = column_headers

    def get_column(self, header):
        try:
            return self.column_headers.index(header)
        except ValueError:
            # Handle the case when the header is not found in column_headers
            return None