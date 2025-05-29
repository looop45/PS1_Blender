import bpy

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

def compile_to_glsl(tree):
    output_node = next(n for n in tree.nodes if n.bl_idname == "ps1_output")
    nodes = topological_sort(output_node)

    var_names = {}
    glsl_lines = []

    def resolve_input(sock):
        if not sock.is_linked:
            return default_value_for_socket(sock)
        from_node = sock.links[0].from_node
        from_sock = sock.links[0].from_socket
        return var_names[(from_node.name, from_sock.name)]