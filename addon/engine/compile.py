import bpy
import re

class PS1CompileResult:
    def __init__(self):
        self.glsl_lines = []
        self.uniforms = {}
        self.inputs = set()
        self.output_var = None

    def add_line(self, line):
        self.glsl_lines.append(line)

    def add_uniform(self, name, value):
        self.uniforms[name] = value

    def as_glsl(self):

        main_body = [
            "void main() {",
            *[f"    {line}" for line in self.glsl_lines],
            f"  fragColor = vec4({self.output_var}, 1.0);",
            "}"
        ]

        return "\n".join(main_body)

def topological_sort(output_node):
    visited = set()
    order = []

    def visit(node):
        if node in visited:
            return
        visited.add(node)
        for socket in node.inputs:
            if socket.is_linked:
                from_node = socket.links[0].from_node
                visit(from_node)
        order.append(node)

    visit(output_node)
    return(list(reversed(order)))

def get_variable_name(node):
        var_name = node.name
        var_name = var_name.lower()
        var_name = re.sub('[^A-Za-z0-9]+', '', var_name)
        return var_name

def compile_tree(tree):
    result = PS1CompileResult()

    output_node = next(n for n in tree.nodes if n.bl_idname == "ps1_output")
    nodes = topological_sort(output_node)
    var_map = {}

    for node in nodes:
        if not hasattr(node, "compile"):
            continue  # skip nodes without a compile method

        input_vars = {}
        for input_socket in node.inputs:
            if input_socket.is_linked:
                from_node = input_socket.links[0].from_node
                from_socket = input_socket.links[0].from_socket
                key = f"{get_variable_name(from_node)}_{from_socket.name}"
                input_vars[input_socket.name] = var_map.get(key, "vec3(0.0)")
            else:
                value = getattr(input_socket, "default_value", None)
                if isinstance(value, (float, int)):
                    input_vars[input_socket.name] = f"{value:.3f}"
                elif hasattr(value, "__len__"):
                    input_vars[input_socket.name] = f"vec3({value[0]:.3f}, {value[1]:.3f}, {value[2]:.3f})"
                else:
                    input_vars[input_socket.name] = "vec3(0.0)"

        try:
            code, output_var = node.compile(input_vars)
        except Exception as e:
            print(f"Failed to compile node {node.name}: {e}")
            continue

        result.add_line(code)

        for output_socket in node.outputs:
            key = f"{get_variable_name(node)}_{output_socket.name}"
            var_map[key] = output_var

        if hasattr(node, "required_uniforms"):
            for name, value in node.required_uniforms().items():
                result.add_uniform(name, value)

        result.output_var = output_var  # track final output var for fragColor

    return result