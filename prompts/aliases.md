🏗️ Implementation Strategy:
python@classmethod
def register_yaml_aliases(cls):
    """Register YAML tag aliases for backward compatibility"""
    
    # Handle !<Slit> tags
    def slit_constructor(loader, node):
        values = loader.construct_mapping(node, deep=True)
        if 'shape' in values and 'contour2d' not in values:
            values['contour2d'] = values.pop('shape')  # Convert field name
        return CoolingSlit.from_dict(values)
    
    yaml.add_constructor('!<Slit>', slit_constructor)
    
    # Handle !<Shape2D> tags  
    def shape2d_constructor(loader, node):
        values = loader.construct_mapping(node, deep=True)
        return Contour2D.from_dict(values)
    
    yaml.add_constructor('!<Shape2D>', shape2d_constructor)
🎯 What You Need To Do:

Call the alias registration (once at startup):

python   Bitter.register_yaml_aliases()
