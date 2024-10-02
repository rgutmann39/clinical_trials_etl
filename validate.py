"""
Module to validate the predictions made by the LLM.
This validation is implemented by checking the accuracy of the LLM against a
gold set of 20 labels
"""
from typing import Mapping
import pandas as pd

# Mapping from NCT ID to list of study interventions, CONTAINS chemo intervention
_GOLD_LABELS_POSITIVE: Mapping[str, str] = {
    "NCT04233866": "Drug: Gemcitabine, Drug: Fluorouracil",
    "NCT00942331": "Drug: Cisplatin, Biological: Bevacizumab",
    "NCT06132958": "Biological: Sacituzumab tirumotecan, Drug: Doxorubicin",
    "NCT02973789": "Device: NovoTTF-200T, Drug: Immune checkpoint inhibitors or docetaxel",
    "NCT05567601": "Drug: DOXIL/CAELYX, Drug: DOXIL/CAELYX",
    "NCT05040360": "Drug: Capecitabine",
    "NCT05610163": "Drug: Capecitabine, Drug: Capecitabine",
    "NCT02166463": "Biological: Bleomycin Sulfate, Drug: Brentuximab Vedotin",
    "NCT02339740": "Drug: Arsenic Trioxide",
    "NCT02112916": "Drug: Cyclophosphamide, Drug: Bortezomib",
}

# Mapping from NCT ID to list of study interventions, DOES NOT CONTAIN chemo intervention
_GOLD_LABELS_NEGATIVE: Mapping[str, str] = {
    "NCT02641639": "Drug: Fosbretabulin tromethamine, Drug: Placebo",
    "NCT03375320": "Drug: Cabozantinib S-malate, Procedure: Computed Tomography",
    "NCT05705401": "Radiation: Standard of Care Adjuvant Breast Radiation, Drug: Standard of Care HER2-targeted Therapy Without Adjuvant Breast Radiation",
    "NCT00379340": "Radiation: 3-Dimensional Conformal Radiation Therapy",
    "NCT05204927": "Drug: Abiraterone with Prednisone or Enzalutamide, Drug: 177Lu-PSMA-I&T",
    "NCT04134260": "Drug: Hormone Therapy, Drug: Apalutamide",
    "NCT02893930": "Drug: Sapanisertib",
    "NCT01575548": "Procedure: Computed Tomography, Procedure: Computed Tomography",
    "NCT03033576": "Biological: Ipilimumab, Biological: Ipilimumab",
    "NCT01901094": "Procedure: Axillary Lymph Node Dissection (ALND), Radiation: Nodal Radiation Therapy",
}

GOLD_LABEL_NCT_IDS = [
    *_GOLD_LABELS_POSITIVE.keys(),
    *_GOLD_LABELS_NEGATIVE.keys(),
]

def test_llm_inferences(inference_df: pd.DataFrame) -> None:
    """Calculate the LLM accuracy for contains_chemo against
    a set of 20 gold labels"""
    # Convert inference_df into dictionary for earier processing
    inference_dict = inference_df.set_index('nctId')['contains_chemo'].to_dict()

    # calculate accuracy among positive gold labels
    num_positive_golds_present, num_positive_golds_correct = 0, 0
    for nctId in _GOLD_LABELS_POSITIVE.keys():
        if nctId in inference_dict:
            num_positive_golds_present += 1
            if inference_dict[nctId]: # check that LLM predicted True for positive golds
                num_positive_golds_correct += 1

    # calculate accuracy among negative gold labels
    num_negative_golds_present, num_negative_golds_correct = 0, 0
    for nctId in _GOLD_LABELS_NEGATIVE.keys():
        if nctId in inference_dict:
            num_negative_golds_present += 1
            if not inference_dict[nctId]: # check that LLM predicted False for negative golds
                num_negative_golds_correct += 1
    
    # Print accuracy among positive golds, negative golds, and combined
    accuracy_positive_golds = round(num_positive_golds_correct / num_positive_golds_present * 100)
    accuracy_negative_golds = round(num_negative_golds_correct / num_negative_golds_present * 100)
    accuracy_combined_golds = round(
        (num_positive_golds_correct + num_negative_golds_correct) / 
        (num_positive_golds_present + num_negative_golds_present) * 100
    )
    print(
        f'Accuracy among positive golds: {accuracy_positive_golds}% ' +
        f'({num_positive_golds_correct} / {num_positive_golds_present})'
    )
    print(
        f'Accuracy among negative golds: {accuracy_negative_golds}% ' +
        f'({num_negative_golds_correct} / {num_negative_golds_present})'
    )
    print(
        f'Accuracy among combined golds: {accuracy_combined_golds}% ' +
        f'({num_positive_golds_correct + num_negative_golds_correct} / ' +
        f'{num_positive_golds_present + num_negative_golds_present})'
    )
