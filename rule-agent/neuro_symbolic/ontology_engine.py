"""
ontology_engine.py

Purpose:
---------
- Define the OWL ontology (engine domain) and all related classes/properties.
- Initialize the reasoner (via owlready2) and provide functions such as get_ontology_info().
- Encapsulate ontology updates and reasoner synchronization.
"""

from owlready2 import get_ontology, Thing, ObjectProperty, sync_reasoner

# Define a constant for the ontology IRI (adjust as needed)
ONTOLOGY_IRI = "http://example.org/engine_ontology.owl"
ONTOLOGY_FILE = "engine_ontology.owl"


def create_ontology():
    """
    Create and initialize the engine ontology with its classes, properties, and instances.
    
    Returns:
        onto (Ontology): The initialized ontology.
    """
    onto = get_ontology(ONTOLOGY_IRI)
    with onto:
        # Define classes
        class Engine(Thing):
            """A general engine."""
            pass

        class OilEngine(Engine):
            """An engine powered by oil."""
            pass

        class ElectricEngine(Engine):
            """An engine powered by electricity."""
            pass

        class EngineComponent(Thing):
            """A component of an engine."""
            pass

        class OilEngineComponent(EngineComponent):
            """A component specific to oil engines."""
            pass

        class ElectricEngineComponent(EngineComponent):
            """A component specific to electric engines."""
            pass

        # Define specific components
        class Piston(OilEngineComponent):
            """A piston, part of an oil engine."""
            pass

        class OilPump(OilEngineComponent):
            """An oil pump, part of an oil engine."""
            pass

        class Battery(ElectricEngineComponent):
            """A battery, used in an electric engine."""
            pass

        class Motor(ElectricEngineComponent):
            """A motor, a component of an electric engine."""
            pass

        # Define the object property that links a component to an engine it may cause to fail
        class CausesFailure(ObjectProperty):
            """
            Object property stating that an engine component can cause failure in an engine.
            Domain: EngineComponent, Range: Engine.
            """
            domain = [EngineComponent]
            range = [Engine]

    # Create instances and define relationships
    with onto:
        piston = Piston("piston_1")
        oil_pump = OilPump("oil_pump_1")
        battery = Battery("battery_1")
        motor = Motor("motor_1")
        oil_engine = OilEngine("oil_engine_1")
        electric_engine = ElectricEngine("electric_engine_1")

        # Define relationships between components and engines via CausesFailure property
        piston.CausesFailure.append(oil_engine)
        oil_pump.CausesFailure.append(oil_engine)
        battery.CausesFailure.append(electric_engine)
        motor.CausesFailure.append(electric_engine)

    # Save the ontology to a file
    onto.save(file=ONTOLOGY_FILE)

    # Run the reasoner to infer new knowledge within the ontology
    update_ontology(onto)

    return onto


def update_ontology(onto):
    """
    Update (synchronize) the ontology by running the reasoner.
    This will infer new knowledge and update relationships if applicable.
    
    Args:
        onto (Ontology): The ontology to be updated.
    """
    with onto:
        sync_reasoner()  # Uses the default reasoner (e.g., HermiT)
    onto.save(file=ONTOLOGY_FILE)


def get_ontology_info(onto):
    """
    Retrieve a summary of ontology contents including classes, individuals, and object properties.
    
    Args:
        onto (Ontology): The ontology from which to extract information.
        
    Returns:
        info (str): A string summarizing the ontology's classes, individuals, and properties.
    """
    info_lines = ["Ontology Information:"]
    
    # List defined classes
    info_lines.append("\nClasses:")
    for cls in onto.classes():
        info_lines.append(f" - {cls.name}")
    
    # List individuals (with their primary type if available)
    info_lines.append("\nIndividuals:")
    for ind in onto.individuals():
        # Use first type if available
        type_info = ind.is_a[0].name if ind.is_a else "Unknown"
        info_lines.append(f" - {ind.name} (Type: {type_info})")
    
    # List object properties
    info_lines.append("\nObject Properties:")
    for prop in onto.object_properties():
        info_lines.append(f" - {prop.name}")

    return "\n".join(info_lines)


# For quick testing and direct module execution:
if __name__ == "__main__":
    ontology = create_ontology()
    print(get_ontology_info(ontology))
