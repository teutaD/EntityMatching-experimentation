from ontoaligner import ontology, encoder
from ontoaligner.aligner import SimpleFuzzySMLightweight
from ontoaligner.utils import metrics, xmlify
import json

task = ontology.MaterialInformationMatOntoOMDataset()
print("Test Task:", task)

dataset = task.collect(
    source_ontology_path="assets/MI-MatOnto/mi_ontology.xml",
    target_ontology_path="assets/MI-MatOnto/matonto_ontology.xml",
    reference_matching_path="assets/MI-MatOnto/matchings.xml"
)

encoder_model = encoder.ConceptParentLightweightEncoder()
encoder_output = encoder_model(
        source=dataset['source'],
        target=dataset['target']
)
model = SimpleFuzzySMLightweight(fuzzy_sm_threshold=0.2)
matchings = model.generate(input_data=encoder_output)
evaluation = metrics.evaluation_report(
    predicts=matchings,
    references=dataset['reference']
)
print("Evaluation Report:", json.dumps(evaluation, indent=4))