import yaml
from python_magnetgeo.Helix import Helix

def create_test_yaml():
    """Create test YAML files to debug the issue"""
    
    # Create a simple helix
    helix = Helix(
        name="H1", r=[10, 15], z=[0, 50], cutwidth=2.0,
        odd=False, dble=True, modelaxi=None,
        model3d=None, shape=None
    )
    
    print("1. Creating YAML with default yaml.dump():")
    with open("H1_default.yaml", "w") as f:
        yaml.dump(helix, f)

    # Read it back to see what it looks like
    with open("H1_default.yaml", "r") as f:
        content = f.read()
        print("Content:")
        print(content)
        print("-" * 50)
    
if __name__ == "__main__":
    create_test_yaml()
