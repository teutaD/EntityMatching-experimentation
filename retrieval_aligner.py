import json

# Import modules from OntoAligner
from ontoaligner import ontology, encoder
from ontoaligner.utils import metrics, xmlify
from ontoaligner.aligner import SBERTRetrieval
from ontoaligner.postprocess import retriever_postprocessor

task = ontology.MaterialInformationMatOntoOMDataset()
print("Test Task:", task)

dataset = task.collect(
    source_ontology_path="assets/MI-MatOnto/mi_ontology.xml",
    target_ontology_path="assets/MI-MatOnto/matonto_ontology.xml",
    reference_matching_path="assets/MI-MatOnto/matchings.xml"
)

# Initialize the encoder model and encode the dataset.
encoder_model = encoder.ConceptParentLightweightEncoder()
encoder_output = encoder_model(source=dataset['source'], target=dataset['target'])

# Initialize retrieval model
model = SBERTRetrieval(device='cpu', top_k=10)
model.load(path="all-MiniLM-L6-v2")

# Generate matchings
matchings = model.generate(input_data=encoder_output)

# Post-process matchings
matchings = retriever_postprocessor(matchings)

# Evaluate matchings
evaluation = metrics.evaluation_report(
    predicts=matchings,
    references=dataset['reference']
)

# Print evaluation report
print("Evaluation Report:", json.dumps(evaluation, indent=4))