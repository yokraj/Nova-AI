"""Blender Physics & Simulation Domain Executor.

Generates BPY scripts for Rigid Body dynamics, Collision physics, Cloth simulations,
Soft Body physics, Force Fields, Fluid (Mantaflow) domain/flow configuration,
and physical simulation state observation.
"""

from typing import Any, Dict, Set

ALLOWED_COLLISION_SHAPES: Set[str] = {
    "BOX",
    "SPHERE",
    "CAPSULE",
    "CYLINDER",
    "CONVEX_HULL",
    "MESH",
}

ALLOWED_FORCE_FIELD_TYPES: Set[str] = {
    "FORCE",
    "WIND",
    "VORTEX",
    "TURBULENCE",
}

ALLOWED_FLUID_TYPES: Set[str] = {
    "DOMAIN",
    "FLOW",
    "EFFECTOR",
}

SUPPORTED_PHYSICS_ACTIONS: Set[str] = {
    # Rigid Body (7)
    "add_rigid_body",
    "remove_rigid_body",
    "set_rigid_body_properties",
    "set_rigid_body_mass",
    "set_rigid_body_collision_shape",
    "get_rigid_body_state",
    "configure_rigid_body_world",

    # Collision (4)
    "add_collision_physics",
    "remove_collision_physics",
    "set_collision_properties",
    "get_collision_state",

    # Cloth (4)
    "add_cloth_simulation",
    "remove_cloth_simulation",
    "set_cloth_properties",
    "get_cloth_state",

    # Soft Body (4)
    "add_soft_body_simulation",
    "remove_soft_body_simulation",
    "set_soft_body_properties",
    "get_soft_body_state",

    # Fluid (4)
    "add_fluid_simulation",
    "set_fluid_domain",
    "set_fluid_flow",
    "get_fluid_state",

    # Force Fields (4)
    "add_force_field",
    "remove_force_field",
    "set_force_field_properties",
    "get_force_field_state",
}


class BlenderPhysicsExecutor:
    """Domain executor for Blender physics and simulation actions."""

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Constructs machine-readable BPY script for physics operations."""
        if action_type not in SUPPORTED_PHYSICS_ACTIONS:
            raise ValueError(f"Unsupported physics action: '{action_type}'")

        # ---------------------------------------------------------
        # Rigid Body System (7 Actions)
        # ---------------------------------------------------------
        if action_type == "add_rigid_body":
            name = params.get("object_name") or params.get("name", "Cube")
            body_type = params.get("rigid_type") or params.get("type", "ACTIVE").upper()
            mass = params.get("mass", 1.0)
            shape = params.get("collision_shape", "BOX").upper()
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_rigid_body')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    obj.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                f"    bpy.ops.rigidbody.object_add(type='{body_type}')\n"
                "    if obj.rigid_body:\n"
                f"        obj.rigid_body.mass = {mass}\n"
                f"        obj.rigid_body.collision_shape = '{shape}'\n"
                f"    print('NOVA_ACTION_SUCCESS::add_rigid_body::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_rigid_body::Object {name} not found.')\n"
            )

        elif action_type == "remove_rigid_body":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_rigid_body')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    obj.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                "    bpy.ops.rigidbody.object_remove()\n"
                f"    print('NOVA_ACTION_SUCCESS::remove_rigid_body::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_rigid_body::Object {name} not found.')\n"
            )

        elif action_type == "set_rigid_body_properties":
            name = params.get("object_name") or params.get("name", "Cube")
            mass = params.get("mass")
            shape = params.get("collision_shape")
            b_type = params.get("rigid_type")
            m_assign = f"obj.rigid_body.mass = {mass}\n" if mass is not None else ""
            s_assign = f"obj.rigid_body.collision_shape = '{shape}'.upper()\n" if shape else ""
            t_assign = f"obj.rigid_body.type = '{b_type}'.upper()\n" if b_type else ""
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_rigid_body_properties')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.rigid_body:\n"
                f"    {m_assign}"
                f"    {s_assign}"
                f"    {t_assign}"
                f"    print('NOVA_ACTION_SUCCESS::set_rigid_body_properties::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_rigid_body_properties::Object {name} has no rigid body.')\n"
            )

        elif action_type == "set_rigid_body_mass":
            name = params.get("object_name") or params.get("name", "Cube")
            mass = params["mass"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_rigid_body_mass')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.rigid_body:\n"
                f"    obj.rigid_body.mass = {mass}\n"
                f"    print('NOVA_ACTION_SUCCESS::set_rigid_body_mass::{mass}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_rigid_body_mass::Object {name} has no rigid body.')\n"
            )

        elif action_type == "set_rigid_body_collision_shape":
            name = params.get("object_name") or params.get("name", "Cube")
            shape = params["collision_shape"].upper()
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_rigid_body_collision_shape')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.rigid_body:\n"
                f"    obj.rigid_body.collision_shape = '{shape}'\n"
                f"    print('NOVA_ACTION_SUCCESS::set_rigid_body_collision_shape::{shape}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_rigid_body_collision_shape::Object {name} has no rigid body.')\n"
            )

        elif action_type == "get_rigid_body_state":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_rigid_body_state')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.rigid_body:\n"
                "    rb = obj.rigid_body\n"
                "    info = {'name': obj.name, 'type': rb.type, 'mass': rb.mass, 'shape': rb.collision_shape}\n"
                "    print('RIGID_BODY_STATE_JSON:' + json.dumps(info))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_rigid_body_state::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_rigid_body_state::Object {name} has no rigid body.')\n"
            )

        elif action_type == "configure_rigid_body_world":
            substeps = params.get("substeps", 10)
            solver_iters = params.get("solver_iterations", 10)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::configure_rigid_body_world')\n"
                "scene = bpy.context.scene\n"
                "if not scene.rigidbody_world:\n"
                "    bpy.ops.rigidbody.world_add()\n"
                "rbw = scene.rigidbody_world\n"
                "if rbw:\n"
                f"    rbw.substeps_per_frame = {substeps}\n"
                f"    rbw.solver_iterations = {solver_iters}\n"
                f"    print('NOVA_ACTION_SUCCESS::configure_rigid_body_world::{substeps}')\n"
                "else:\n"
                "    print('NOVA_ACTION_ERROR::configure_rigid_body_world::Failed creating rigid body world.')\n"
            )

        # ---------------------------------------------------------
        # Collision Physics (4 Actions)
        # ---------------------------------------------------------
        elif action_type == "add_collision_physics":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_collision_physics')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.new(name='Collision', type='COLLISION')\n"
                f"    print('NOVA_ACTION_SUCCESS::add_collision_physics::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_collision_physics::Object {name} not found.')\n"
            )

        elif action_type == "remove_collision_physics":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_collision_physics')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.get('Collision')\n"
                "    if mod:\n"
                "        obj.modifiers.remove(mod)\n"
                f"        print('NOVA_ACTION_SUCCESS::remove_collision_physics::{name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::remove_collision_physics::Collision modifier missing.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_collision_physics::Object {name} not found.')\n"
            )

        elif action_type == "set_collision_properties":
            name = params.get("object_name") or params.get("name", "Cube")
            d_val = params.get("damping", 0.1)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_collision_properties')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Collision'):\n"
                "    col_mod = obj.modifiers.get('Collision')\n"
                f"    if hasattr(col_mod, 'settings'): col_mod.settings.damping = {d_val}\n"
                f"    print('NOVA_ACTION_SUCCESS::set_collision_properties::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_collision_properties::Object {name} missing collision.')\n"
            )

        elif action_type == "get_collision_state":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_collision_state')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "has_col = obj is not None and any(m.type == 'COLLISION' for m in obj.modifiers)\n"
                "print('COLLISION_STATE_JSON:' + json.dumps({'has_collision': has_col}))\n"
                "print('NOVA_ACTION_SUCCESS::get_collision_state::' + str(has_col))\n"
            )

        # ---------------------------------------------------------
        # Cloth Simulation (4 Actions)
        # ---------------------------------------------------------
        elif action_type == "add_cloth_simulation":
            name = params.get("object_name") or params.get("name", "Plane")
            mass = params.get("mass", 0.3)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_cloth_simulation')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.new(name='Cloth', type='CLOTH')\n"
                f"    mod.settings.mass = {mass}\n"
                f"    print('NOVA_ACTION_SUCCESS::add_cloth_simulation::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_cloth_simulation::Object {name} not found.')\n"
            )

        elif action_type == "remove_cloth_simulation":
            name = params.get("object_name") or params.get("name", "Plane")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_cloth_simulation')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.get('Cloth')\n"
                "    if mod:\n"
                "        obj.modifiers.remove(mod)\n"
                f"        print('NOVA_ACTION_SUCCESS::remove_cloth_simulation::{name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::remove_cloth_simulation::Cloth modifier not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_cloth_simulation::Object {name} not found.')\n"
            )

        elif action_type == "set_cloth_properties":
            name = params.get("object_name") or params.get("name", "Plane")
            mass = params.get("mass")
            quality = params.get("quality")
            m_code = f"mod.settings.mass = {mass}\n" if mass is not None else ""
            q_code = f"mod.settings.quality = {quality}\n" if quality is not None else ""
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_cloth_properties')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Cloth'):\n"
                "    mod = obj.modifiers['Cloth']\n"
                f"    {m_code}"
                f"    {q_code}"
                f"    print('NOVA_ACTION_SUCCESS::set_cloth_properties::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_cloth_properties::Cloth modifier not found.')\n"
            )

        elif action_type == "get_cloth_state":
            name = params.get("object_name") or params.get("name", "Plane")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_cloth_state')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Cloth'):\n"
                "    mod = obj.modifiers['Cloth']\n"
                "    info = {'mass': mod.settings.mass, 'quality': mod.settings.quality}\n"
                "    print('CLOTH_STATE_JSON:' + json.dumps(info))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_cloth_state::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_cloth_state::Cloth modifier not found.')\n"
            )

        # ---------------------------------------------------------
        # Soft Body Simulation (4 Actions)
        # ---------------------------------------------------------
        elif action_type == "add_soft_body_simulation":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_soft_body_simulation')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.new(name='Softbody', type='SOFT_BODY')\n"
                f"    print('NOVA_ACTION_SUCCESS::add_soft_body_simulation::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_soft_body_simulation::Object {name} not found.')\n"
            )

        elif action_type == "remove_soft_body_simulation":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_soft_body_simulation')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.get('Softbody')\n"
                "    if mod:\n"
                "        obj.modifiers.remove(mod)\n"
                f"        print('NOVA_ACTION_SUCCESS::remove_soft_body_simulation::{name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::remove_soft_body_simulation::Softbody modifier not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_soft_body_simulation::Object {name} not found.')\n"
            )

        elif action_type == "set_soft_body_properties":
            name = params.get("object_name") or params.get("name", "Cube")
            friction = params.get("friction", 0.5)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_soft_body_properties')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Softbody'):\n"
                "    mod = obj.modifiers['Softbody']\n"
                f"    mod.settings.friction = {friction}\n"
                f"    print('NOVA_ACTION_SUCCESS::set_soft_body_properties::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_soft_body_properties::Softbody modifier not found.')\n"
            )

        elif action_type == "get_soft_body_state":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_soft_body_state')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Softbody'):\n"
                "    mod = obj.modifiers['Softbody']\n"
                "    info = {'friction': mod.settings.friction}\n"
                "    print('SOFT_BODY_STATE_JSON:' + json.dumps(info))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_soft_body_state::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_soft_body_state::Softbody modifier not found.')\n"
            )

        # ---------------------------------------------------------
        # Fluid Simulation (4 Actions)
        # ---------------------------------------------------------
        elif action_type == "add_fluid_simulation":
            name = params.get("object_name") or params.get("name", "Cube")
            fluid_type = params.get("fluid_type", "DOMAIN").upper()
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_fluid_simulation')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mod = obj.modifiers.new(name='Fluid', type='FLUID')\n"
                f"    mod.fluid_type = '{fluid_type}'\n"
                f"    print('NOVA_ACTION_SUCCESS::add_fluid_simulation::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_fluid_simulation::Object {name} not found.')\n"
            )

        elif action_type == "set_fluid_domain":
            name = params.get("object_name") or params.get("name", "Cube")
            domain_type = params.get("domain_type", "GAS").upper()
            res = params.get("resolution", 32)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_fluid_domain')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Fluid'):\n"
                "    mod = obj.modifiers['Fluid']\n"
                "    mod.fluid_type = 'DOMAIN'\n"
                "    if hasattr(mod, 'domain_settings'):\n"
                f"        mod.domain_settings.domain_type = '{domain_type}'\n"
                f"        mod.domain_settings.resolution_max = {res}\n"
                f"    print('NOVA_ACTION_SUCCESS::set_fluid_domain::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_fluid_domain::Fluid domain missing.')\n"
            )

        elif action_type == "set_fluid_flow":
            name = params.get("object_name") or params.get("name", "Cube")
            flow_type = params.get("flow_type", "SMOKE").upper()
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_fluid_flow')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Fluid'):\n"
                "    mod = obj.modifiers['Fluid']\n"
                "    mod.fluid_type = 'FLOW'\n"
                "    if hasattr(mod, 'flow_settings'):\n"
                f"        mod.flow_settings.flow_type = '{flow_type}'\n"
                f"    print('NOVA_ACTION_SUCCESS::set_fluid_flow::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_fluid_flow::Fluid flow missing.')\n"
            )

        elif action_type == "get_fluid_state":
            name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_fluid_state')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.modifiers.get('Fluid'):\n"
                "    mod = obj.modifiers['Fluid']\n"
                "    info = {'fluid_type': mod.fluid_type}\n"
                "    print('FLUID_STATE_JSON:' + json.dumps(info))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_fluid_state::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_fluid_state::Fluid modifier missing.')\n"
            )

        # ---------------------------------------------------------
        # Force Fields (4 Actions)
        # ---------------------------------------------------------
        elif action_type == "add_force_field":
            field_type = params.get("field_type", "WIND").upper()
            x, y, z = params.get("location", (0.0, 0.0, 0.0))
            strength = params.get("strength", 1.0)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_force_field')\n"
                f"bpy.ops.object.effector_add(type='{field_type}', location=({x}, {y}, {z}))\n"
                "field_obj = bpy.context.active_object\n"
                "if field_obj and field_obj.field:\n"
                f"    field_obj.field.strength = {strength}\n"
                f"    print('NOVA_ACTION_SUCCESS::add_force_field::' + field_obj.name)\n"
                "else:\n"
                "    print('NOVA_ACTION_ERROR::add_force_field::Failed creating force field.')\n"
            )

        elif action_type == "remove_force_field":
            name = params.get("object_name") or params.get("name", "Field")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_force_field')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.data.objects.remove(obj, do_unlink=True)\n"
                f"    print('NOVA_ACTION_SUCCESS::remove_force_field::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_force_field::Force field {name} not found.')\n"
            )

        elif action_type == "set_force_field_properties":
            name = params.get("object_name") or params.get("name", "Field")
            strength = params.get("strength")
            flow = params.get("flow")
            s_code = f"obj.field.strength = {strength}\n" if strength is not None else ""
            f_code = f"obj.field.flow = {flow}\n" if flow is not None else ""
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_force_field_properties')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.field:\n"
                f"    {s_code}"
                f"    {f_code}"
                f"    print('NOVA_ACTION_SUCCESS::set_force_field_properties::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_force_field_properties::Field {name} missing.')\n"
            )

        elif action_type == "get_force_field_state":
            name = params.get("object_name") or params.get("name", "Field")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_force_field_state')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.field:\n"
                "    info = {'type': obj.field.type, 'strength': obj.field.strength}\n"
                "    print('FORCE_FIELD_STATE_JSON:' + json.dumps(info))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_force_field_state::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_force_field_state::Field {name} missing.')\n"
            )

        raise ValueError(f"No BPY template for action '{action_type}'")
