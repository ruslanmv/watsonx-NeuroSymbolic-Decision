"""
ml_model.py

Purpose:
---------
- Generate training data from the ontology (functions like training_data_generator()).
- Train an ML model (using scikit-learn’s LogisticRegression as an example).
- Convert natural language input into logical forms (with function convert_to_logical()).
"""

import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# Helper functions for verbalization

def verbalize_individual(individual):
    """
    Convert an ontology individual's name to a human-friendly format.
    For example, "piston_1" becomes "Piston".
    """
    return individual.name.split('_')[0].capitalize() if hasattr(individual, 'name') else str(individual)

def verbalize_property(prop):
    """
    Convert an ontology property's name to a natural language phrase.
    This example assumes the primary property is 'CausesFailure' and returns a fixed phrase.
    """
    # Customize based on your property names.
    if "CausesFailure" in prop.name:
        return "causes failure of"
    return prop.name.lower()

# Function to extract elements from the ontology

def get_all_elements(onto):
    """
    Extract relevant elements (individuals and object properties) from the ontology.
    
    Args:
        onto: The owlready2 ontology.
        
    Returns:
        A dictionary with keys 'individuals' and 'properties'.
    """
    individuals = list(onto.individuals())
    properties = list(onto.object_properties())
    return {"individuals": individuals, "properties": properties}

# Training data generation

def training_data_generator(onto):
    """
    Generate training data based on the ontology.
    
    For each object property, evaluate potential subject-object pairs (provided they belong to the
    property's domain and range) and produce examples:
      - A positive example if the relationship exists.
      - A negative example (prefixed with "not") if it does not.
    
    Returns:
        data: A list of tuples (natural_language_statement, logical_form)
    """
    data = []
    elements = get_all_elements(onto)
    individuals = elements["individuals"]
    properties = elements["properties"]
    
    for prop in properties:
        # Only process properties that have defined domain and range
        if not (hasattr(prop, "domain") and hasattr(prop, "range")):
            continue
        
        # Loop over every potential subject/object pair
        for subj in individuals:
            for obj in individuals:
                # Check if subject belongs to one of the property's domain classes
                # and if object belongs to one of the property's range classes.
                domain_match = any(isinstance(subj, domain) for domain in prop.domain)
                range_match = any(isinstance(obj, range_) for range_ in prop.range)
                if domain_match and range_match:
                    # Build the logical form
                    logical_form = f"{subj.name}.{prop.name}({obj.name})"
                    # Check if the relationship actually exists in the ontology.
                    is_true = obj in prop[subj]
                    
                    if is_true:
                        nl_statement = f"{verbalize_individual(subj)} {verbalize_property(prop)} {verbalize_individual(obj)}"
                        data.append((nl_statement, logical_form))
                    else:
                        # For false relationships, optionally add a negated example.
                        nl_statement_negative = f"{verbalize_individual(subj)} does not {verbalize_property(prop)} {verbalize_individual(obj)}"
                        logical_form_negative = f"not {logical_form}"
                        data.append((nl_statement_negative, logical_form_negative))
                    
    return data

# Model training functions

def model_generator(training_data):
    """
    Train a logistic regression model to map natural language statements to logical forms.
    
    Args:
        training_data: A list of tuples (natural_language_statement, logical_form)
        
    Returns:
        model: A trained LogisticRegression model.
        vectorizer: A CountVectorizer fitted to the natural language statements.
    """
    vectorizer = CountVectorizer()
    X_train = vectorizer.fit_transform([pair[0] for pair in training_data])
    y_train = [pair[1] for pair in training_data]
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model, vectorizer

def modelizer(onto):
    """
    Generate training data from the ontology and train the ML model.
    
    Args:
        onto: The owlready2 ontology which has been initialized and updated.
    
    Returns:
        model: The trained LogisticRegression model.
        vectorizer: The fitted CountVectorizer used for text transformation.
    """
    training_data = training_data_generator(onto)
    model, vectorizer = model_generator(training_data)
    return model, vectorizer

def convert_to_logical(statement, model, vectorizer):
    """
    Convert a natural language statement into its corresponding logical form using the trained model.
    
    Args:
        statement (str): A natural language input statement.
        model: The trained LogisticRegression model.
        vectorizer: The fitted CountVectorizer.
    
    Returns:
        logical_form (str): The predicted logical form.
    """
    X_test = vectorizer.transform([statement])
    predicted = model.predict(X_test)
    logical_form = predicted[0]
    return logical_form

# Example testing block.
if __name__ == "__main__":
    # For testing this module, you should load your ontology (e.g., via ontology_engine.create_ontology())
    # Example (uncomment and modify according to your project environment):
    # from ontology_engine import create_ontology
    # onto = create_ontology()
    # model, vectorizer = modelizer(onto)
    # test_statement = "Piston causes failure of Oil engine"
    # logical = convert_to_logical(test_statement, model, vectorizer)
    # print("Predicted logical form:", logical)
    print("ml_model.py loaded. Integrate with your ontology to generate training data and train the model.")
