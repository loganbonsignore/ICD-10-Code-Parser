# ICD-10 Code Parser

### Project Overview
These scripts parse JSON documents containing ICD-10 medical codes provided by the Center for Medicare & Medicaid Services (CMS). ICD-10 documents provided by CMS are originally in XML format and have been converted to JSON for this project.

**execute_pcs_index_query.py** - Command line program to query the 2021 PCS Index./n
**PCS_Index.json** - Official 2021 PCS index document in JSON format.

**execute_pcs_table_query.py** - Class definitions of pcs table query tool and example usage./n
**PCS_Tables.json** - Official 2021 PCS table data in JSON format.

**pcs_index_test_and_parse.py** - Built in test for *execute_pcs_index_query.py*. Uses PCS_Index.json.

### Tools Used
Python

### Data Sources
Official ICD-10 data sets can be found at [cms.gov](https://www.cms.gov/Medicare/Coding/ICD10).