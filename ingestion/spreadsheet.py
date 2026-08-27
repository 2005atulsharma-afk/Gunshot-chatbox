import pandas as pd


def extract_spreadsheet(path):
    """
    Extract CSV/XLSX/XLS data into searchable text.
    """

    extension = path.suffix.lower()

    results = []

    if extension == ".csv":

        dataframe = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False
        )

        text = dataframe.to_string(
            index=False
        )

        if text.strip():

            results.append(
                {
                    "text": text,
                    "page": None,
                    "location": "CSV file",
                }
            )

        return results

    # --------------------------------------------------------
    # Excel
    # --------------------------------------------------------

    workbook = pd.ExcelFile(path)

    for sheet_name in workbook.sheet_names:

        dataframe = pd.read_excel(
            path,
            sheet_name=sheet_name,
            dtype=str
        )

        dataframe = dataframe.fillna("")

        text = dataframe.to_string(
            index=False
        )

        if text.strip():

            results.append(
                {
                    "text": text,
                    "page": None,
                    "location": f"Excel sheet: {sheet_name}",
                }
            )

    return results