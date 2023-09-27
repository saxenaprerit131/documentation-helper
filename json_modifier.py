import os
import json
import traceback

# Define the JSON element to add
new_element = {
    "override": {
        "label": "Additional Withholding",
        "list": [
            {
                "codeValue": "AA",
                "shortName": "Additional $ amount withholding",
                "helpText": "Additional $ amount to withhold each Payroll",
                "default": True,
                "defaultValue": "$0",
                "advancedOptionDefault": True,
                "format": "^[\\$]{0,1}[0-9,\\,]{0,9}(?:[.]{1}[0-9]{1,2}){0,1}$",
                "textMasks": {
                    "prefix": "$",
                    "includeThousandsSeparator": True,
                    "allowDecimal": True,
                    "integerLimit": 7,
                    "decimalLimit": 2,
                },
            },
            {
                "codeValue": "AP",
                "shortName": "Additional % amount withholding",
                "advancedOption": True,
                "defaultValue": "0%",
                "format": "^100(\\.0{0,2})? *%?$|^\\d{1,2}(\\.\\d{1,2})? *%?$",
                "textMasks": {
                    "prefix": "",
                    "suffix": "%",
                    "includeThousandsSeparator": False,
                    "allowDecimal": True,
                    "integerLimit": 3,
                    "decimalLimit": 2,
                },
            },
            {
                "codeValue": "FA",
                "shortName": "Flat $ Amount",
                "advancedOption": True,
                "defaultValue": "$0",
                "format": "^[\\$]{0,1}[0-9,\\,]{0,9}(?:[.]{1}[0-9]{1,2}){0,1}$",
                "textMasks": {
                    "prefix": "$",
                    "includeThousandsSeparator": True,
                    "allowDecimal": True,
                    "integerLimit": 7,
                    "decimalLimit": 2,
                },
            },
            {
                "codeValue": "FP",
                "shortName": "Flat % Amount",
                "advancedOption": True,
                "defaultValue": "0%",
                "format": "^100(\\.0{0,2})? *%?$|^\\d{1,2}(\\.\\d{1,2})? *%?$",
                "textMasks": {
                    "prefix": "",
                    "suffix": "%",
                    "includeThousandsSeparator": False,
                    "allowDecimal": True,
                    "integerLimit": 3,
                    "decimalLimit": 2,
                },
            },
        ],
    }
}


def endsWithBlankLine(input_file):
    with open(input_file, "rb") as file:
        file.seek(-1, 2)
        last_char = file.read(1)
        return last_char == b'\n'


# Directory containing JSON files
input_dir = r'C:\SBSNEX\statutory_jurisdiction_service\src\jurisdictions\locals\PA'

# Loop through each JSON file in the directory
for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(input_dir, filename)
        addBlankLine = endsWithBlankLine(file_path)
        try:
            # Read and parse JSON
            with open(file_path, "r", encoding='utf-8') as input_file:
                data = json.load(input_file)

            # Check if this file has 'filingPolicies' to update. If not, skip the file
            if "filingPolicies" not in data:
                print(f"Skipping file: {file_path} (No filingPolicies element found.)")
                continue

            for filingPolicy in data["filingPolicies"]:
                # Check if this file has 'taxes' element to update. If not, skip the file
                if "taxes" not in filingPolicy:
                    print(f"Skipping file: {file_path} (No taxes element found.)")
                    continue

                # Find each 'tax' element and append new_element at the end
                for tax in filingPolicy["taxes"]:
                
                    if "override" in tax:
                        print(f"Skipping file: {file_path} (Override element found.)")
                        continue
                    
                    if tax["codeValue"] == 'LIT-ER':
                        print(f"Skipping file: {file_path} (LIT-ER element found.)")
                        continue

                    tax.update(new_element)

                    # Write back to the same file
                    with open(file=file_path, mode="w", encoding='utf-8') as output_file:
                        json.dump(data, output_file, ensure_ascii=False, indent=4)
                        if addBlankLine:
                            output_file.write('\n')
        except Exception as e:
            # Write the exception message in console
            print("An exception occurred in file: ", file_path, " Message: ", str(e))
