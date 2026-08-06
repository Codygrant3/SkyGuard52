import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUT_DIR = Path(r"D:\Skyguard52\Saved\Screenshots\AAA_L88_Blockout")
EXPORT = Path(
    r"D:\Skyguard52\Content\Skyguard\Meshes\Source\L88"
    r"\yak52_l88_silhouette_blockout.glb"
)
MASTER_BLEND = Path(
    r"D:\Skyguard52\Content\Skyguard\Meshes\Source\L88"
    r"\YAK52_L88_MASTER_BLOCKOUT.blend"
)
REPORT = OUT_DIR / "L88_SILHOUETTE_REPORT.json"
MARKER_REPORT = Path(r"D:\Skyguard52\Saved\Reports\L88_MARKERS.json")

TARGET_LENGTH = 7.68
TARGET_SPAN = 9.30
TARGET_HEIGHT = 2.70


def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.metallic = metallic
    mat.roughness = roughness
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (*color, 1.0)
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
    return mat


def add_micro_surface(mat, scale=85.0, strength=0.08, roughness_variation=0.06):
    """Add restrained procedural surface breakup for validation renders.

    The GLB still carries the canonical PBR values; this node detail keeps the
    Blender beauty/cockpit proofs from reading as flat Roblox primitives while
    the authored texture bake is deferred to the production-art pass.
    """
    if not mat.use_nodes:
        return
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    if principled is None:
        return
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = "L88_MicroNoise"
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.68
    bump = nodes.new("ShaderNodeBump")
    bump.name = "L88_MicroBump"
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.012
    rough = nodes.new("ShaderNodeMapRange")
    rough.name = "L88_RoughnessVariation"
    rough.inputs["From Min"].default_value = 0.25
    rough.inputs["From Max"].default_value = 0.75
    rough.inputs["To Min"].default_value = max(0.05, mat.roughness - roughness_variation)
    rough.inputs["To Max"].default_value = min(0.98, mat.roughness + roughness_variation)
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    links.new(noise.outputs["Fac"], rough.inputs["Value"])
    links.new(rough.outputs["Result"], principled.inputs["Roughness"])


def smooth_mesh(obj, weighted=True):
    if obj is None or obj.type != "MESH":
        return
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if weighted:
        try:
            modifier = obj.modifiers.new("L88_WeightedNormals", "WEIGHTED_NORMAL")
            modifier.keep_sharp = True
            modifier.weight = 50
        except Exception:
            pass


def apply_l88_semantic_pbr_uv_layers(hero_objects):
    """Attach deterministic semantic-family and UV-readiness metadata.

    This is deliberately additive: it does not rename objects, change their
    transforms, or alter the measured envelope.  A named UV layer gives the
    eventual authored bake a stable target while the custom property records
    the material family used by the review manifest.
    """
    def family_for(obj):
        name = obj.name
        if name.startswith("GEO_Gunner") or name.startswith("GEO_Igla"):
            return "weapon_ads"
        if name.startswith("GEO_Pilot") or name.startswith("GEO_RearSoldier"):
            return "crew"
        if "Canopy" in name:
            return "glass"
        if any(
            token in name
            for token in (
                "RearSeat",
                "Harness",
                "Console",
                "Panel",
                "Gauge",
                "Pedal",
                "Cockpit",
                "Throttle",
                "Trim",
                "Switch",
                "Radio",
                "Latch",
                "Wiring",
                "MapLight",
                "Buckle",
                "Sidewall",
                "CabinRib",
                "Warning",
                "Placard",
                "Rail",
                "Belt",
            )
        ):
            return "cockpit_trim"
        if any(token in name for token in ("Wheel", "Tire", "Rubber")):
            return "rubber"
        if any(token in name for token in ("Prop", "Engine", "Brake", "Gear", "Torque", "Radial", "Strut", "Cowl")):
            return "engine_metal"
        if any(token in name for token in ("Livery", "Roundel", "Stripe", "NavLamp")):
            return "livery_paint"
        if name.endswith("Wings") or "Tail" in name or name == "GEO_Airframe":
            return "painted_metal"
        return "painted_metal"

    uv_name = "UV_L88_0"
    family_counts = {}
    uv_count = 0
    for obj in hero_objects:
        mesh = obj.data
        layer = mesh.uv_layers.get(uv_name)
        if layer is None:
            source = mesh.uv_layers.active
            layer = mesh.uv_layers.new(name=uv_name)
            if source is not None and len(source.data) == len(layer.data):
                for index, source_loop in enumerate(source.data):
                    layer.data[index].uv = source_loop.uv
        obj["L88_MaterialFamily"] = family_for(obj)
        obj["L88_UVLayer"] = uv_name
        family_counts[obj["L88_MaterialFamily"]] = family_counts.get(obj["L88_MaterialFamily"], 0) + 1
        uv_count += 1
    return {"uv_layer": uv_name, "mesh_count": uv_count, "family_counts": family_counts}


def build_l88_rear_weapon_ads_markers(root):
    """Create editor/source markers without adding render meshes to the GLB."""
    specs = (
        ("SO_RearWeaponMount", (-0.32, -0.64, 0.60), "weapon_mount"),
        ("SO_ADSEye", (-0.18, -0.64, 0.99), "ads_eye"),
        ("SO_RearEye", (-0.65, -0.64, 1.02), "rear_eye"),
    )
    markers = []
    for name, location, role in specs:
        marker = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(marker)
        marker.empty_display_type = "ARROWS"
        marker.empty_display_size = 0.10
        marker.location = location
        marker.rotation_euler = (0.0, 0.0, 0.0)
        marker.parent = root
        marker["L88_MarkerRole"] = role
        marker["L88_ForwardAxis"] = "+X"
        markers.append(marker)
    return markers


def mesh_object(name, vertices, faces, mat):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def set_origin_world(obj, world_location):
    """Rebase an object's origin without moving its rendered geometry."""

    previous_cursor = bpy.context.scene.cursor.location.copy()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.scene.cursor.location = world_location
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    bpy.context.scene.cursor.location = previous_cursor
    obj.select_set(False)


def fuselage(name, sections, segments, mat, open_top_x_range=None):
    vertices = []
    for x, radius_y, radius_z, z_offset in sections:
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            vertices.append(
                (
                    x,
                    math.cos(angle) * radius_y,
                    z_offset + math.sin(angle) * radius_z,
                )
            )
    faces = []
    rings = len(sections)
    for ring in range(rings - 1):
        for index in range(segments):
            nxt = (index + 1) % segments
            if open_top_x_range is not None:
                x_mid = 0.5 * (sections[ring][0] + sections[ring + 1][0])
                angle_mid = 2.0 * math.pi * (index + 0.5) / segments
                # The real Yak-52 has an open rear station. Leave a broad
                # top-side aperture through the cockpit so the hero camera
                # can read the seat, consoles, and instrument panel instead
                # of looking into a closed primitive tube.
                if (
                    open_top_x_range[0] <= x_mid <= open_top_x_range[1]
                    and math.sin(angle_mid) > 0.48
                ):
                    continue
            a = ring * segments + index
            b = ring * segments + nxt
            c = (ring + 1) * segments + nxt
            d = (ring + 1) * segments + index
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(range(segments))))
    start = (rings - 1) * segments
    faces.append(tuple(start + index for index in range(segments)))
    return mesh_object(name, vertices, faces, mat)


def prism_from_planform(name, outline, z_center, thickness, mat, dihedral=0.0, camber=0.0):
    x_values = [point[0] for point in outline]
    x_min = min(x_values)
    x_max = max(x_values)

    def profile(x):
        normalized = 0.5 if abs(x_max - x_min) < 1e-6 else (x - x_min) / (x_max - x_min)
        normalized = max(0.0, min(1.0, normalized))
        edge_factor = 0.78 + 0.22 * math.sin(math.pi * normalized)
        camber_offset = camber * math.sin(math.pi * normalized)
        half = thickness * edge_factor * 0.5
        return z_center - half + camber_offset * 0.18, z_center + half + camber_offset

    vertices = []
    for x, y in outline:
        bottom, _ = profile(x)
        vertices.append((x, y, bottom + dihedral * abs(y)))
    for x, y in outline:
        _, top = profile(x)
        vertices.append((x, y, top + dihedral * abs(y)))
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    obj = mesh_object(name, vertices, faces, mat)
    bevel = obj.modifiers.new("EdgeSoftening", "BEVEL")
    bevel.width = min(thickness * 0.35, 0.035)
    bevel.segments = 3
    return obj


def twisted_propeller_pair(name, axis_x, stations, mat):
    """Build a tapered, pitched two-blade propeller as one gameplay mesh.

    The geometry is authored around the engine axis so Unreal can spin it
    directly without compensating for a DCC-only origin offset.
    """

    vertices = []
    faces = []
    section_size = 4
    blade_ranges = []
    for blade_sign in (-1.0, 1.0):
        blade_start = len(vertices)
        for radius, chord, thickness, pitch_degrees in stations:
            pitch = math.radians(pitch_degrees)
            cos_pitch = math.cos(pitch)
            sin_pitch = math.sin(pitch)
            for local_x, local_y in (
                (-thickness * 0.50, -chord * 0.50),
                (thickness * 0.50, -chord * 0.50),
                (thickness * 0.50, chord * 0.50),
                (-thickness * 0.50, chord * 0.50),
            ):
                pitched_x = local_x * cos_pitch - local_y * sin_pitch
                pitched_y = local_x * sin_pitch + local_y * cos_pitch
                vertices.append(
                    (
                        pitched_x,
                        blade_sign * pitched_y,
                        blade_sign * radius,
                    )
                )
        blade_ranges.append((blade_start, len(stations)))

    for blade_start, station_count in blade_ranges:
        faces.append(tuple(blade_start + index for index in (3, 2, 1, 0)))
        for station_index in range(station_count - 1):
            current = blade_start + station_index * section_size
            following = current + section_size
            for edge in range(section_size):
                next_edge = (edge + 1) % section_size
                faces.append(
                    (
                        current + edge,
                        current + next_edge,
                        following + next_edge,
                        following + edge,
                    )
                )
        end = blade_start + (station_count - 1) * section_size
        faces.append(tuple(end + index for index in (0, 1, 2, 3)))

    obj = mesh_object(name, vertices, faces, mat)
    obj.location = (axis_x, 0.0, 0.0)
    obj["L88_PivotRole"] = "prop_axis"
    obj["L88_RotationAxis"] = "+X"
    return obj


def tapered_oleo_strut(name, start, end, radii, mat, segments=24):
    """Create a smooth tapered oleo strut while preserving one named mesh."""

    start_v = Vector(start)
    end_v = Vector(end)
    axis = (end_v - start_v).normalized()
    helper = Vector((0.0, 0.0, 1.0))
    if abs(axis.dot(helper)) > 0.92:
        helper = Vector((0.0, 1.0, 0.0))
    basis_a = axis.cross(helper).normalized()
    basis_b = axis.cross(basis_a).normalized()
    vertices = []
    faces = []
    ring_count = len(radii)

    for ring_index, radius in enumerate(radii):
        factor = ring_index / max(1, ring_count - 1)
        center = start_v.lerp(end_v, factor)
        for segment_index in range(segments):
            angle = 2.0 * math.pi * segment_index / segments
            offset = basis_a * (math.cos(angle) * radius)
            offset += basis_b * (math.sin(angle) * radius)
            vertices.append(tuple(center + offset - start_v))

    faces.append(tuple(reversed(range(segments))))
    for ring_index in range(ring_count - 1):
        current = ring_index * segments
        following = current + segments
        for segment_index in range(segments):
            next_segment = (segment_index + 1) % segments
            faces.append(
                (
                    current + segment_index,
                    current + next_segment,
                    following + next_segment,
                    following + segment_index,
                )
            )
    final_ring = (ring_count - 1) * segments
    faces.append(tuple(final_ring + index for index in range(segments)))
    obj = mesh_object(name, vertices, faces, mat)
    obj.location = tuple(start_v)
    obj["L88_PivotRole"] = "landing_gear_attachment"
    return obj


def vertical_fin(name, points, half_width, mat):
    vertices = [(x, -half_width, z) for x, z in points]
    vertices += [(x, half_width, z) for x, z in points]
    count = len(points)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    obj = mesh_object(name, vertices, faces, mat)
    bevel = obj.modifiers.new("FinEdgeSoftening", "BEVEL")
    bevel.width = 0.022
    bevel.segments = 3
    return obj


def add_cylinder(name, radius, depth, location, rotation, mat, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("EdgeSoftening", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 3
    return obj


def rod_between(name, start, end, radius, mat, vertices=32):
    """Create a beveled hard-surface rod between two world-space points."""
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    length = direction.length
    if length <= 1e-6:
        raise ValueError("rod endpoints are coincident: " + name)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=length,
        location=(start + end) * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("EdgeSoftening", "BEVEL")
    bevel.width = min(radius * 0.45, 0.018)
    bevel.segments = 3
    return obj


def canopy_shell(name, sections, segments, mat):
    """Build the upper half of a tapered tandem canopy as a thin shell.

    The section contract is (x, half_width, half_height, center_z).  Keeping
    the lower edge open lets the rear station read as an open gunner cockpit,
    while the forward shell and separate rails establish a real canopy rather
    than a closed primitive sphere.
    """
    vertices = []
    for x, half_width, half_height, center_z in sections:
        for index in range(segments + 1):
            angle = math.pi * index / segments
            vertices.append(
                (
                    x,
                    math.cos(angle) * half_width,
                    center_z + math.sin(angle) * half_height,
                )
            )
    faces = []
    stride = segments + 1
    for ring in range(len(sections) - 1):
        for index in range(segments):
            a = ring * stride + index
            b = a + 1
            c = (ring + 1) * stride + index + 1
            d = (ring + 1) * stride + index
            faces.append((a, b, c, d))
    obj = mesh_object(name, vertices, faces, mat)
    solidify = obj.modifiers.new("CanopyShellThickness", "SOLIDIFY")
    solidify.thickness = 0.008
    solidify.offset = 0.0
    bevel = obj.modifiers.new("CanopyEdgeSoftening", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 2
    subdivision = obj.modifiers.new("CanopySurfaceContinuity", "SUBSURF")
    subdivision.subdivision_type = "CATMULL_CLARK"
    subdivision.levels = 1
    subdivision.render_levels = 1
    return obj


def canopy_bow(name, x, half_width, base_z, crown_z, mat, tube_radius=0.018, samples=20):
    """Build one continuous tubular bow that follows the canopy crown.

    A single joined mesh avoids the old three-cube goalpost silhouette while
    retaining a real hard-surface frame with circular section and smooth
    normals.  The path is kept in the canopy's y/z plane so it cannot cross
    the pilot or rear-gunner sightline.
    """
    path = []
    for index in range(samples + 1):
        theta = math.pi * index / samples
        path.append(Vector((x, math.cos(theta) * half_width, base_z + math.sin(theta) * (crown_z - base_z))))
    vertices = []
    sides = 12
    for index, point in enumerate(path):
        if index == 0:
            tangent = path[1] - path[0]
        elif index == len(path) - 1:
            tangent = path[-1] - path[-2]
        else:
            tangent = path[index + 1] - path[index - 1]
        tangent.normalize()
        basis_u = Vector((1.0, 0.0, 0.0))
        basis_v = tangent.cross(basis_u).normalized()
        for side_index in range(sides):
            angle = 2.0 * math.pi * side_index / sides
            offset = tube_radius * (math.cos(angle) * basis_u + math.sin(angle) * basis_v)
            vertices.append(tuple(point + offset))
    faces = []
    for ring in range(len(path) - 1):
        for side_index in range(sides):
            nxt = (side_index + 1) % sides
            a = ring * sides + side_index
            b = ring * sides + nxt
            c = (ring + 1) * sides + nxt
            d = (ring + 1) * sides + side_index
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(range(sides))))
    start = (len(path) - 1) * sides
    faces.append(tuple(start + side_index for side_index in range(sides)))
    obj = mesh_object(name, vertices, faces, mat)
    bevel = obj.modifiers.new("CanopyBowEdgeSoftening", "BEVEL")
    bevel.width = min(tube_radius * 0.25, 0.006)
    bevel.segments = 2
    return obj


def wing_root_fairing(name, side, mat):
    """Loft a thin wing-root blend from fuselage skin into the wing.

    The fairing deliberately tapers to nearly zero at both x ends.  Its full
    vertical thickness stays below 0.14 m, preventing the detached UV-sphere
    pod read that the previous blockout produced in the beauty view.
    """
    sections = (
        (-0.95, 0.010, 0.008),
        (-0.78, 0.038, 0.018),
        (-0.55, 0.078, 0.032),
        (-0.25, 0.108, 0.045),
        (0.05, 0.112, 0.046),
        (0.35, 0.082, 0.034),
        (0.62, 0.042, 0.020),
        (0.82, 0.010, 0.008),
    )
    vertices = []
    sides = 32
    for x, radius_y, radius_z in sections:
        blend = math.sin(math.pi * (x - sections[0][0]) / (sections[-1][0] - sections[0][0]))
        center_y = side * (0.61 + 0.10 * blend)
        center_z = -0.30 + 0.012 * math.cos(math.pi * (x - sections[0][0]) / (sections[-1][0] - sections[0][0]))
        for index in range(sides):
            angle = 2.0 * math.pi * index / sides
            vertices.append((x, center_y + side * math.cos(angle) * radius_y, center_z + math.sin(angle) * radius_z))
    faces = []
    for ring in range(len(sections) - 1):
        for index in range(sides):
            nxt = (index + 1) % sides
            a = ring * sides + index
            b = ring * sides + nxt
            c = (ring + 1) * sides + nxt
            d = (ring + 1) * sides + index
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(range(sides))))
    start = (len(sections) - 1) * sides
    faces.append(tuple(start + index for index in range(sides)))
    obj = mesh_object(name, vertices, faces, mat)
    bevel = obj.modifiers.new("WingRootFairingSoftening", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 3
    subdivision = obj.modifiers.new("WingRootFairingContinuity", "SUBSURF")
    subdivision.subdivision_type = "CATMULL_CLARK"
    subdivision.levels = 1
    subdivision.render_levels = 1
    return obj


def glove_palm(name, center, mat):
    """Build a compact tapered palm from wrist to knuckle line.

    The hand is kept as one named hero mesh so the L88 import contract stays
    stable.  Elliptical rings give the palm a human taper and a readable
    leather silhouette instead of a single UV-sphere cue.
    """
    cx, cy, cz = center
    sections = (
        (-0.16, 0.055, 0.052),
        (-0.09, 0.085, 0.066),
        (0.00, 0.112, 0.080),
        (0.09, 0.118, 0.078),
        (0.16, 0.082, 0.060),
    )
    sides = 20
    vertices = []
    for offset_x, radius_y, radius_z in sections:
        for index in range(sides):
            angle = 2.0 * math.pi * index / sides
            vertices.append(
                (
                    cx + offset_x,
                    cy + math.cos(angle) * radius_y,
                    cz + math.sin(angle) * radius_z,
                )
            )
    faces = []
    for ring in range(len(sections) - 1):
        for index in range(sides):
            nxt = (index + 1) % sides
            a = ring * sides + index
            b = ring * sides + nxt
            c = (ring + 1) * sides + nxt
            d = (ring + 1) * sides + index
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(range(sides))))
    start = (len(sections) - 1) * sides
    faces.append(tuple(start + index for index in range(sides)))
    obj = mesh_object(name, vertices, faces, mat)
    bevel = obj.modifiers.new("GlovePalmEdgeSoftening", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 3
    subdivision = obj.modifiers.new("GlovePalmContinuity", "SUBSURF")
    subdivision.subdivision_type = "CATMULL_CLARK"
    subdivision.levels = 1
    subdivision.render_levels = 1
    return obj


def add_uv(name, location, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64,
        ring_count=32,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def add_cube(name, location, scale, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("EdgeSoftening", "BEVEL")
    bevel.width = 0.045
    bevel.segments = 4
    obj.data.materials.append(mat)
    return obj


def add_wheel(name, location, scale, rubber, hub):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=scale * 0.72,
        minor_radius=scale * 0.26,
        major_segments=48,
        minor_segments=16,
        location=location,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    tire = bpy.context.object
    tire.name = name + "_Tire"
    tire.data.materials.append(rubber)
    add_cylinder(
        name + "_Hub",
        scale * 0.46,
        scale * 0.32,
        location,
        (math.radians(90.0), 0.0, 0.0),
        hub,
        vertices=48,
    )


def add_torus(name, major_radius, minor_radius, location, rotation, mat):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=96,
        minor_segments=20,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def world_bounds(objects):
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    minimum = Vector(
        (
            min(point.x for point in points),
            min(point.y for point in points),
            min(point.z for point in points),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in points),
            max(point.y for point in points),
            max(point.z for point in points),
        )
    )
    return minimum, maximum


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat(
        "-Z",
        "Y",
    ).to_euler()


def add_area(name, location, energy, size, color, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)


def add_camera(name, location, target, lens=58.0, orthographic=False, scale=12.0):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    if orthographic:
        data.type = "ORTHO"
        data.ortho_scale = scale
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def configure_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    if scene.world is None:
        scene.world = bpy.data.worlds.new("L88_World")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.025, 0.045, 0.075, 1.0)
    background.inputs["Strength"].default_value = 0.42
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def build_aircraft():
    paint = material("M_L88_PaintedMetal", (0.32, 0.38, 0.42), 0.72, 0.34)
    underside = material("M_L88_Underside", (0.50, 0.57, 0.60), 0.62, 0.38)
    dark_metal = material("M_L88_EngineMetal", (0.055, 0.065, 0.075), 0.82, 0.26)
    glass = material("M_L88_CanopyGlass", (0.06, 0.17, 0.24), 0.12, 0.06)
    # Treat the greenhouse as a real thin transparent surface in Blender's
    # current material API.  The alpha/transmission values are kept restrained
    # so the frame, cockpit volume, and exterior reflections remain legible.
    try:
        glass.surface_render_method = "BLENDED"
        glass.use_transparency_overlap = False
        glass.show_transparent_back = True
        glass.use_transparent_shadow = False
    except Exception:
        pass
    glass_principled = glass.node_tree.nodes.get("Principled BSDF")
    if glass_principled:
        # Keep the canopy readable in the stills without turning it into an
        # opaque blue wall in the rear-gunner view.
        if "Transmission Weight" in glass_principled.inputs:
            glass_principled.inputs["Transmission Weight"].default_value = 0.72
        if "Coat Weight" in glass_principled.inputs:
            glass_principled.inputs["Coat Weight"].default_value = 0.28
        if "Coat Roughness" in glass_principled.inputs:
            glass_principled.inputs["Coat Roughness"].default_value = 0.08
        if "IOR" in glass_principled.inputs:
            glass_principled.inputs["IOR"].default_value = 1.45
        glass_principled.inputs["Alpha"].default_value = 0.32
    canopy_frame = material("M_L88_CanopyFrame", (0.11, 0.14, 0.15), 0.24, 0.46)
    add_micro_surface(canopy_frame, scale=145.0, strength=0.035, roughness_variation=0.045)
    cockpit = material("M_L88_Cockpit", (0.18, 0.23, 0.20), 0.35, 0.58)
    rubber = material("M_L88_Rubber", (0.018, 0.021, 0.024), 0.0, 0.82)
    leather = material("M_L88_SeatLeather", (0.16, 0.075, 0.035), 0.0, 0.78)
    harness_red = material("M_L88_HarnessRed", (0.56, 0.025, 0.018), 0.0, 0.62)
    instrument = material("M_L88_InstrumentBlack", (0.018, 0.022, 0.024), 0.18, 0.52)
    gauge_face = material("M_L88_GaugeFace", (0.62, 0.66, 0.62), 0.08, 0.42)
    needle = material("M_L88_Needle", (0.85, 0.12, 0.025), 0.0, 0.35)
    rifle_metal = material("M_L88_RifleMetal", (0.035, 0.042, 0.045), 0.78, 0.30)
    rifle_wood = material("M_L88_RifleWood", (0.22, 0.075, 0.028), 0.0, 0.58)
    # A black leather glove still needs a readable value edge against the
    # rifle and cockpit.  Keep it dark, but lift the base value and coat so
    # the knuckle/palm silhouette survives the seated and ADS views.
    glove = material("M_L88_Glove", (0.006, 0.008, 0.011), 0.02, 0.68)
    sleeve = material("M_L88_Sleeve", (0.055, 0.075, 0.038), 0.0, 0.84)
    skin = material("M_L88_Skin", (0.46, 0.24, 0.16), 0.0, 0.58)
    helmet = material("M_L88_FlightHelmet", (0.16, 0.18, 0.16), 0.08, 0.52)
    igla_green = material("M_L88_IglaGreen", (0.16, 0.20, 0.075), 0.16, 0.66)
    livery_blue = material("M_L88_LiveryBlue", (0.025, 0.12, 0.34), 0.28, 0.30)
    livery_yellow = material("M_L88_LiveryYellow", (0.92, 0.58, 0.045), 0.12, 0.34)
    livery_white = material("M_L88_LiveryWhite", (0.82, 0.86, 0.84), 0.18, 0.30)
    nav_red = material("M_L88_NavRed", (0.62, 0.012, 0.008), 0.05, 0.22)
    nav_green = material("M_L88_NavGreen", (0.02, 0.44, 0.09), 0.05, 0.22)
    add_micro_surface(paint, scale=120.0, strength=0.055, roughness_variation=0.045)
    add_micro_surface(underside, scale=95.0, strength=0.045, roughness_variation=0.04)
    add_micro_surface(cockpit, scale=70.0, strength=0.065, roughness_variation=0.08)
    add_micro_surface(leather, scale=55.0, strength=0.11, roughness_variation=0.10)
    add_micro_surface(rifle_metal, scale=150.0, strength=0.035, roughness_variation=0.035)
    add_micro_surface(rifle_wood, scale=38.0, strength=0.09, roughness_variation=0.08)
    add_micro_surface(glove, scale=90.0, strength=0.08, roughness_variation=0.08)
    add_micro_surface(helmet, scale=105.0, strength=0.035, roughness_variation=0.05)
    add_micro_surface(igla_green, scale=90.0, strength=0.045, roughness_variation=0.05)
    add_micro_surface(livery_blue, scale=115.0, strength=0.028, roughness_variation=0.035)
    add_micro_surface(livery_yellow, scale=95.0, strength=0.025, roughness_variation=0.035)
    add_micro_surface(livery_white, scale=105.0, strength=0.022, roughness_variation=0.03)

    root = bpy.data.objects.new("YAK52_L88_ROOT", None)
    bpy.context.scene.collection.objects.link(root)

    sections = (
        (-3.42, 0.12, 0.15, 0.05),
        (-3.12, 0.24, 0.30, 0.04),
        (-2.65, 0.36, 0.45, 0.02),
        (-2.10, 0.47, 0.58, 0.01),
        (-1.45, 0.57, 0.72, 0.03),
        (-0.55, 0.67, 0.82, 0.06),
        (0.35, 0.74, 0.86, 0.06),
        (1.25, 0.81, 0.88, 0.04),
        (2.10, 0.87, 0.90, 0.01),
        (2.72, 0.91, 0.91, 0.00),
        (2.98, 0.90, 0.89, 0.00),
    )
    parts = [fuselage("GEO_Airframe", sections, 64, paint, open_top_x_range=(-1.30, 0.98))]

    cowl = add_cylinder(
        "GEO_EngineCowling",
        0.90,
        0.64,
        (3.30, 0.0, 0.0),
        (0.0, math.radians(90.0), 0.0),
        paint,
        vertices=96,
    )
    parts.append(cowl)
    engine_face = add_cylinder(
        "GEO_EngineFace",
        0.72,
        0.08,
        (3.63, 0.0, 0.0),
        (0.0, math.radians(90.0), 0.0),
        dark_metal,
        vertices=96,
    )
    parts.append(engine_face)
    parts.append(add_torus("GEO_CowlNoseFillet", 0.74, 0.055, (3.64, 0.0, 0.0), (0.0, math.radians(90.0), 0.0), dark_metal))
    for radial_index in range(9):
        radial_angle = 2.0 * math.pi * radial_index / 9.0
        radial_y = math.cos(radial_angle) * 0.50
        radial_z = math.sin(radial_angle) * 0.50
        parts.append(
            add_cylinder(
                f"GEO_RadialCylinder_{radial_index}",
                0.070,
                0.20,
                (3.70, radial_y, radial_z),
                (0.0, math.radians(90.0), 0.0),
                dark_metal,
                vertices=32,
            )
        )
    # Pass21 9: visible radial-engine plumbing.  The collector ring and three
    # representative pushrods add believable mechanical depth behind the
    # propeller without exploding draw calls with hidden internal hardware.
    parts.append(add_torus("GEO_EngineExhaustCollector", 0.58, 0.035, (3.56, 0.0, 0.0), (0.0, math.radians(90.0), 0.0), dark_metal))
    for pushrod_index, pushrod_angle in enumerate((0.35, 2.45, 4.55)):
        pushrod_y = math.cos(pushrod_angle) * 0.43
        pushrod_z = math.sin(pushrod_angle) * 0.43
        parts.append(
            rod_between(
                f"GEO_EnginePushrod_{pushrod_index}",
                (3.60, pushrod_y * 0.42, pushrod_z * 0.42),
                (3.76, pushrod_y, pushrod_z),
                0.018,
                dark_metal,
                vertices=20,
            )
        )

    wing_outline = (
        (1.10, 0.0),
        (0.78, 3.70),
        (0.62, 4.25),
        (0.40, 4.55),
        (0.14, 4.65),
        (-0.12, 4.63),
        (-0.42, 4.43),
        (-0.64, 4.08),
        (-1.08, 0.0),
        (-0.64, -4.08),
        (-0.42, -4.43),
        (-0.12, -4.63),
        (0.14, -4.65),
        (0.40, -4.55),
        (0.62, -4.25),
        (0.78, -3.70),
    )
    parts.append(
        prism_from_planform(
            "GEO_Wings",
            wing_outline,
            -0.36,
            0.18,
            underside,
            dihedral=0.05,
            camber=0.055,
        )
    )
    for side in (-1.0, 1.0):
        parts.append(add_cube(f"GEO_AileronBreak_{'L' if side < 0 else 'R'}", (0.10, side * 2.95, -0.255), (0.018, 0.82, 0.010), dark_metal))
        parts.append(add_cube(f"GEO_FlapBreak_{'L' if side < 0 else 'R'}", (-0.54, side * 1.92, -0.255), (0.018, 0.72, 0.010), dark_metal))

    tail_outline = (
        (-2.54, 0.0),
        (-2.70, 1.16),
        (-2.86, 1.48),
        (-3.10, 1.66),
        (-3.34, 1.58),
        (-3.50, 1.28),
        (-3.53, 0.0),
        (-3.50, -1.28),
        (-3.34, -1.58),
        (-3.10, -1.66),
        (-2.86, -1.48),
        (-2.70, -1.16),
    )
    parts.append(
        prism_from_planform(
            "GEO_HorizontalTail",
            tail_outline,
            0.10,
            0.13,
            paint,
            camber=0.025,
        )
    )
    parts.append(add_cube("GEO_ElevatorBreak_L", (-3.16, -0.88, 0.18), (0.018, 0.68, 0.014), dark_metal))
    parts.append(add_cube("GEO_ElevatorBreak_R", (-3.16, 0.88, 0.18), (0.018, 0.68, 0.014), dark_metal))
    fin_points = (
        (-3.49, 0.08),
        (-3.44, 0.62),
        (-3.28, 1.26),
        (-3.07, 1.50),
        (-2.82, 1.52),
        (-2.62, 1.34),
        (-2.48, 0.72),
        (-2.46, 0.08),
    )
    parts.append(vertical_fin("GEO_VerticalTail", fin_points, 0.07, paint))
    # Pass21 8: discrete control-surface hinge lines.  These are authored as
    # separate meshes so production ailerons/elevators can inherit them or be
    # replaced without cutting into the primary lifting-surface meshes.
    parts.append(rod_between("GEO_WingHinge_L", (0.05, -1.35, -0.25), (-0.28, -3.70, -0.23), 0.012, dark_metal, vertices=20))
    parts.append(rod_between("GEO_WingHinge_R", (0.05, 1.35, -0.25), (-0.28, 3.70, -0.23), 0.012, dark_metal, vertices=20))
    parts.append(rod_between("GEO_TailHinge_L", (-3.05, -0.28, 0.17), (-3.25, -1.28, 0.17), 0.010, dark_metal, vertices=20))
    parts.append(rod_between("GEO_TailHinge_R", (-3.05, 0.28, 0.17), (-3.25, 1.28, 0.17), 0.010, dark_metal, vertices=20))

    # Forward canopy shell; rear gunner station remains open with the sliding
    # rear panel parked aft.  The sectioned shell follows the tandem canopy
    # profile instead of reading as a closed UV-sphere primitive.
    parts.append(
        canopy_shell(
            "GEO_FrontCanopyGlass",
            (
                (-0.48, 0.36, 0.17, 0.72),
                (-0.20, 0.48, 0.30, 0.72),
                (0.18, 0.58, 0.39, 0.70),
                (0.56, 0.61, 0.42, 0.68),
                (0.92, 0.53, 0.34, 0.64),
                (1.24, 0.32, 0.19, 0.57),
            ),
            48,
            glass,
        )
    )
    parts.append(canopy_bow("GEO_CanopyBow_0p18", 0.18, 0.58, 0.68, 1.08, canopy_frame, tube_radius=0.012, samples=32))
    parts.append(canopy_bow("GEO_CanopyBow_0p76", 0.76, 0.54, 0.66, 1.04, canopy_frame, tube_radius=0.012, samples=32))
    for bow_x in (0.18, 0.76):
        parts.append(add_cylinder(f"GEO_CanopyHinge_{bow_x}_L", 0.034, 0.12, (bow_x, -0.62, 0.68), (math.radians(90.0), 0.0, 0.0), canopy_frame, vertices=24))
        parts.append(add_cylinder(f"GEO_CanopyHinge_{bow_x}_R", 0.034, 0.12, (bow_x, 0.62, 0.68), (math.radians(90.0), 0.0, 0.0), canopy_frame, vertices=24))
        # Small sill latches keep the curved bows mechanically grounded
        # without recreating the former rectangular goalpost frame.
        parts.append(rod_between(f"GEO_CanopySeal_{bow_x}_L", (bow_x - 0.035, -0.58, 0.64), (bow_x + 0.035, -0.58, 0.64), 0.010, canopy_frame))
        parts.append(rod_between(f"GEO_CanopySeal_{bow_x}_R", (bow_x - 0.035, 0.58, 0.64), (bow_x + 0.035, 0.58, 0.64), 0.010, canopy_frame))
    parts.append(add_cube("GEO_CockpitTub", (-0.12, 0.0, 0.20), (1.52, 0.52, 0.34), cockpit))
    parts.append(add_cube("GEO_RearCockpitRim_L", (-0.56, -0.58, 0.57), (0.68, 0.028, 0.042), canopy_frame))
    parts.append(add_cube("GEO_RearCockpitRim_R", (-0.56, 0.58, 0.57), (0.68, 0.028, 0.042), canopy_frame))
    # The fixed canopy rails stop at the forward cockpit bulkhead.  Leaving
    # the rear station free of a cross-body rail is essential for a believable
    # open gunner view and prevents the hero camera from looking through a
    # square cage.
    parts.append(
        canopy_shell(
            "GEO_RearCanopyGlass_Stowed",
            (
                (-2.00, 0.24, 0.11, 0.50),
                (-1.82, 0.40, 0.17, 0.54),
                (-1.55, 0.50, 0.21, 0.57),
                (-1.25, 0.52, 0.22, 0.58),
                (-0.95, 0.46, 0.19, 0.58),
                (-0.72, 0.34, 0.14, 0.57),
            ),
            48,
            glass,
        )
    )
    # Canopy perimeter hardware gives the glass a believable load path and
    # makes the sliding/open rear-station mechanic legible in exterior views.
    # Keep the load path above/outboard of the gunner eye line.  The previous
    # low cross-body lip and crown rail read as a cage in the seated view and
    # cut through the rifle/panel sightline.
    parts.append(rod_between("GEO_CanopyPortRail", (-1.94, -0.54, 0.50), (1.24, -0.48, 0.56), 0.007, canopy_frame))
    parts.append(rod_between("GEO_CanopyStarboardRail", (-1.94, 0.54, 0.50), (1.24, 0.48, 0.56), 0.007, canopy_frame))
    # Rear-gunner first-person hero station.
    parts.append(add_cube("GEO_RearSeatCushion", (-0.72, 0.0, 0.28), (0.38, 0.42, 0.085), leather))
    # Keep the shoulder bolster below the eye line.  The earlier tall slab
    # put the validation camera behind the seatback and hid the station.
    parts.append(add_cube("GEO_RearSeatBack", (-1.04, 0.0, 0.54), (0.075, 0.42, 0.25), leather))
    parts.append(add_cube("GEO_RearHarness_L", (-0.79, -0.19, 0.58), (0.035, 0.035, 0.28), harness_red, rotation=(0.0, math.radians(-22.0), 0.0)))
    parts.append(add_cube("GEO_RearHarness_R", (-0.79, 0.19, 0.58), (0.035, 0.035, 0.28), harness_red, rotation=(0.0, math.radians(22.0), 0.0)))
    parts.append(add_cube("GEO_RearConsole_L", (-0.38, -0.52, 0.30), (0.52, 0.10, 0.15), cockpit))
    parts.append(add_cube("GEO_RearConsole_R", (-0.38, 0.52, 0.30), (0.52, 0.10, 0.15), cockpit))
    parts.append(add_cube("GEO_RearPanel", (0.84, 0.0, 0.58), (0.075, 0.48, 0.34), instrument, rotation=(0.0, math.radians(-8.0), 0.0)))
    parts.append(add_cube("GEO_RearPanelTop", (0.79, 0.0, 0.96), (0.12, 0.50, 0.045), paint))
    for gauge_index, gauge_y in enumerate((-0.34, -0.17, 0.0, 0.17, 0.34)):
        parts.append(add_cylinder(f"GEO_Gauge_{gauge_index}", 0.115, 0.035, (0.73, gauge_y, 0.62), (0.0, math.radians(90.0), 0.0), gauge_face, vertices=32))
        parts.append(add_cylinder(f"GEO_GaugeRim_{gauge_index}", 0.128, 0.018, (0.70, gauge_y, 0.62), (0.0, math.radians(90.0), 0.0), instrument, vertices=32))
        parts.append(add_cube(f"GEO_GaugeNeedle_{gauge_index}", (0.68, gauge_y, 0.64), (0.012, 0.012, 0.075), needle, rotation=(0.0, math.radians(90.0), math.radians(-18.0 + gauge_index * 17.0))))
    parts.append(add_cylinder("GEO_ControlStick", 0.045, 0.52, (-0.58, 0.0, 0.56), (0.0, 0.0, 0.0), dark_metal, vertices=24))
    parts.append(add_uv("GEO_ControlStickGrip", (-0.58, 0.0, 0.84), (0.10, 0.08, 0.13), rubber))
    parts.append(add_cube("GEO_Pedal_L", (0.32, -0.22, -0.02), (0.18, 0.055, 0.035), dark_metal))
    parts.append(add_cube("GEO_Pedal_R", (0.32, 0.22, -0.02), (0.18, 0.055, 0.035), dark_metal))

    # Pass20 rear-cockpit hero kit.  These controls use the existing semantic
    # material library, stable names, and gameplay-friendly pivots rather than
    # introducing a one-off material for every small part.
    parts.append(
        add_cube(
            "GEO_RearThrottleQuadrant",
            (-0.62, -0.49, 0.47),
            (0.20, 0.075, 0.105),
            cockpit,
            rotation=(0.0, math.radians(-8.0), 0.0),
        )
    )
    throttle_lever = rod_between(
        "GEO_RearThrottleLever",
        (-0.64, -0.56, 0.51),
        (-0.48, -0.58, 0.76),
        0.024,
        dark_metal,
        vertices=24,
    )
    set_origin_world(throttle_lever, (-0.64, -0.56, 0.51))
    throttle_lever["L88_PivotRole"] = "throttle_hinge"
    parts.append(throttle_lever)
    parts.append(add_uv("GEO_RearThrottleKnob", (-0.48, -0.58, 0.76), (0.060, 0.045, 0.055), rubber))
    parts.append(
        add_torus(
            "GEO_RearTrimWheel",
            0.115,
            0.018,
            (-0.20, -0.585, 0.48),
            (math.radians(90.0), 0.0, 0.0),
            dark_metal,
        )
    )
    for switch_index, switch_y in enumerate((-0.31, -0.19, -0.07, 0.07, 0.19, 0.31)):
        parts.append(
            add_cylinder(
                f"GEO_RearSwitch_{switch_index}",
                0.018,
                0.065,
                (0.655, switch_y, 0.38),
                (0.0, math.radians(90.0), 0.0),
                harness_red if switch_index in (0, 5) else dark_metal,
                vertices=20,
            )
        )
    parts.append(
        add_cube(
            "GEO_RearRadioBox",
            (-0.02, 0.50, 0.49),
            (0.20, 0.075, 0.115),
            instrument,
            rotation=(0.0, math.radians(4.0), 0.0),
        )
    )
    for knob_index, knob_x in enumerate((-0.10, 0.08)):
        parts.append(
            add_cylinder(
                f"GEO_RearRadioKnob_{knob_index}",
                0.034,
                0.035,
                (knob_x, 0.585, 0.51),
                (math.radians(90.0), 0.0, 0.0),
                rubber,
                vertices=24,
            )
        )
    parts.append(
        rod_between(
            "GEO_RearLatch_L",
            (-0.88, -0.60, 0.62),
            (-0.70, -0.60, 0.66),
            0.018,
            canopy_frame,
            vertices=20,
        )
    )
    parts.append(
        rod_between(
            "GEO_RearLatch_R",
            (-0.88, 0.60, 0.62),
            (-0.70, 0.60, 0.66),
            0.018,
            canopy_frame,
            vertices=20,
        )
    )
    parts.append(
        add_cube(
            "GEO_RearHarnessBuckle",
            (-0.73, 0.0, 0.54),
            (0.045, 0.070, 0.055),
            dark_metal,
            rotation=(0.0, math.radians(8.0), 0.0),
        )
    )
    parts.append(
        rod_between(
            "GEO_RearWiringPort",
            (-0.92, -0.57, 0.40),
            (0.42, -0.57, 0.48),
            0.012,
            rubber,
            vertices=20,
        )
    )
    parts.append(
        rod_between(
            "GEO_RearWiringStarboard",
            (-0.86, 0.57, 0.38),
            (0.40, 0.57, 0.46),
            0.012,
            rubber,
            vertices=20,
        )
    )
    parts.append(
        rod_between(
            "GEO_RearMapLightArm",
            (0.48, 0.44, 0.84),
            (0.33, 0.36, 0.72),
            0.015,
            dark_metal,
            vertices=20,
        )
    )
    parts.append(
        add_cylinder(
            "GEO_RearMapLight",
            0.045,
            0.070,
            (0.31, 0.35, 0.70),
            (math.radians(55.0), 0.0, math.radians(25.0)),
            instrument,
            vertices=24,
        )
    )

    # Pass21 ten-subsystem production-candidate wave, 1-4: rear-station
    # structure, panel hardware, sliding-canopy hardware, and restraint system.
    # These remain separate semantic meshes so Unreal can replace or animate
    # them independently without breaking the aircraft root hierarchy.
    parts.append(add_cube("GEO_RearSidewallPadding_L", (-0.70, -0.505, 0.42), (0.48, 0.025, 0.24), leather))
    parts.append(add_cube("GEO_RearSidewallPadding_R", (-0.70, 0.505, 0.42), (0.48, 0.025, 0.24), leather))
    parts.append(rod_between("GEO_RearCabinRib_L", (-1.12, -0.54, 0.22), (-0.30, -0.54, 0.67), 0.018, canopy_frame, vertices=24))
    parts.append(rod_between("GEO_RearCabinRib_R", (-1.12, 0.54, 0.22), (-0.30, 0.54, 0.67), 0.018, canopy_frame, vertices=24))

    parts.append(add_cube("GEO_RearWarningLampBank", (0.655, 0.0, 0.82), (0.020, 0.22, 0.035), harness_red))
    parts.append(add_cube("GEO_RearPanelPlacard", (0.650, 0.27, 0.91), (0.018, 0.11, 0.025), livery_white))
    parts.append(rod_between("GEO_RearSwitchGuard", (0.62, -0.36, 0.33), (0.62, 0.36, 0.33), 0.010, dark_metal, vertices=20))

    parts.append(add_cylinder("GEO_RearRailRoller_L", 0.035, 0.050, (-1.25, -0.575, 0.58), (math.radians(90.0), 0.0, 0.0), dark_metal, vertices=24))
    parts.append(add_cylinder("GEO_RearRailRoller_R", 0.035, 0.050, (-1.25, 0.575, 0.58), (math.radians(90.0), 0.0, 0.0), dark_metal, vertices=24))
    parts.append(rod_between("GEO_RearRailHandle", (-1.08, 0.60, 0.68), (-0.80, 0.60, 0.70), 0.016, canopy_frame, vertices=24))
    rear_rail_lock = add_cube("GEO_RearRailLock", (-0.72, 0.60, 0.66), (0.040, 0.025, 0.055), dark_metal)
    set_origin_world(rear_rail_lock, (-0.76, 0.60, 0.66))
    rear_rail_lock["L88_PivotRole"] = "canopy_rail_lock"
    parts.append(rear_rail_lock)

    parts.append(rod_between("GEO_RearLapBelt_L", (-0.98, -0.32, 0.52), (-0.72, -0.08, 0.40), 0.025, harness_red, vertices=20))
    parts.append(rod_between("GEO_RearLapBelt_R", (-0.98, 0.32, 0.52), (-0.72, 0.08, 0.40), 0.025, harness_red, vertices=20))
    parts.append(add_cube("GEO_RearBeltAnchor_L", (-1.00, -0.34, 0.50), (0.035, 0.045, 0.045), dark_metal))
    parts.append(add_cube("GEO_RearBeltAnchor_R", (-1.00, 0.34, 0.50), (0.035, 0.045, 0.045), dark_metal))

    # Pass22 crew staging: the Yak-52 is flown by a dedicated front-seat pilot,
    # while the rear soldier operates the detachable rifle/Igla gameplay layer.
    # The crew uses stable body-part names for a later skeletal-mesh replacement;
    # these meshes are visual blocking and must not be mistaken for final rigs.
    parts.append(add_cube("GEO_PilotSeatCushion", (0.18, 0.0, 0.26), (0.34, 0.38, 0.075), leather))
    parts.append(add_cube("GEO_PilotSeatBack", (-0.08, 0.0, 0.54), (0.065, 0.38, 0.26), leather))
    parts.append(add_uv("GEO_PilotTorso", (0.12, 0.0, 0.63), (0.25, 0.28, 0.32), sleeve))
    parts.append(add_uv("GEO_PilotHead", (0.28, 0.0, 1.02), (0.135, 0.125, 0.16), skin))
    parts.append(add_uv("GEO_PilotHelmet", (0.27, 0.0, 1.10), (0.165, 0.155, 0.14), helmet))
    parts.append(rod_between("GEO_PilotArm_L", (0.15, -0.22, 0.75), (0.52, -0.16, 0.55), 0.060, sleeve, vertices=24))
    parts.append(rod_between("GEO_PilotArm_R", (0.15, 0.22, 0.75), (0.52, 0.16, 0.55), 0.060, sleeve, vertices=24))
    parts.append(add_cube("GEO_PilotHarness", (0.10, 0.0, 0.72), (0.035, 0.25, 0.18), harness_red, rotation=(0.0, math.radians(-8.0), 0.0)))

    parts.append(add_uv("GEO_RearSoldierTorso", (-0.72, 0.0, 0.62), (0.26, 0.29, 0.34), sleeve))
    parts.append(add_uv("GEO_RearSoldierHead", (-0.68, 0.0, 1.02), (0.135, 0.125, 0.16), skin))
    parts.append(add_uv("GEO_RearSoldierHelmet", (-0.69, 0.0, 1.10), (0.17, 0.16, 0.145), helmet))
    parts.append(rod_between("GEO_RearSoldierArm_L", (-0.66, -0.22, 0.76), (-0.28, -0.40, 0.71), 0.064, sleeve, vertices=24))
    parts.append(rod_between("GEO_RearSoldierArm_R", (-0.66, 0.20, 0.75), (-0.18, -0.56, 0.81), 0.064, sleeve, vertices=24))
    parts.append(rod_between("GEO_RearSoldierThigh_L", (-0.72, -0.16, 0.43), (-0.40, -0.18, 0.24), 0.085, sleeve, vertices=24))
    parts.append(rod_between("GEO_RearSoldierThigh_R", (-0.72, 0.16, 0.43), (-0.40, 0.18, 0.24), 0.085, sleeve, vertices=24))
    parts.append(add_uv("GEO_RearSoldierTriggerHand", (-0.12, -0.64, 0.82), (0.075, 0.055, 0.070), glove))

    # Rear-gunner cue: a side-mounted rifle held across the open station. It
    # is intentionally a restrained blockout, but the barrel, receiver, iron
    # sight, mount, sleeve, and leather-glove silhouette make the player role
    # unambiguous in the hero validation frame.
    parts.append(
        add_cylinder(
            "GEO_GunnerRifleBarrel",
            0.035,
            1.72,
            (0.56, -0.50, 0.82),
            (0.0, math.radians(90.0), 0.0),
            rifle_metal,
            vertices=32,
        )
    )
    parts.append(add_cube("GEO_GunnerRifleReceiver", (-0.24, -0.50, 0.82), (0.28, 0.075, 0.095), rifle_metal))
    parts.append(
        add_cube(
            "GEO_GunnerRifleStock",
            (-0.63, -0.50, 0.78),
            (0.30, 0.065, 0.075),
            rifle_wood,
            rotation=(0.0, math.radians(-4.0), 0.0),
        )
    )
    parts.append(
        add_cylinder(
            "GEO_GunnerRifleMuzzle",
            0.050,
            0.085,
            (1.45, -0.50, 0.82),
            (0.0, math.radians(90.0), 0.0),
            rifle_metal,
            vertices=32,
        )
    )
    # Align the front post to the rear aperture centerline for the dedicated
    # ADS proof; the post must remain visible through the peep instead of
    # disappearing below the sight picture.
    parts.append(add_cube("GEO_GunnerRifleFrontSight", (0.74, -0.50, 0.99), (0.025, 0.025, 0.085), rifle_metal))
    parts.append(add_torus("GEO_GunnerRifleRearSightAperture", 0.045, 0.010, (-0.18, -0.50, 0.99), (0.0, math.radians(90.0), 0.0), rifle_metal,))
    parts.append(
        add_cube(
            "GEO_GunnerRifleMagazine",
            (-0.22, -0.50, 0.66),
            (0.075, 0.050, 0.16),
            rifle_metal,
            rotation=(0.0, math.radians(-12.0), 0.0),
        )
    )
    parts.append(add_cube("GEO_GunnerSleeve", (-0.18, -0.38, 0.70), (0.22, 0.10, 0.12), sleeve, rotation=(0.0, math.radians(-14.0), 0.0)))
    # Stop the flight sleeve at the wrist so the dark leather palm remains
    # visible in the weapon-hero frame instead of being swallowed by one long
    # pale rod.
    parts.append(rod_between("GEO_GunnerForearm", (-0.28, -0.40, 0.71), (0.15, -0.55, 0.81), 0.095, sleeve))
    # The palm sits on the barrel centerline after the port-side station
    # offset.  A tapered ring-built palm and bent capsule-like fingers keep the
    # hand readable as a leather glove instead of a group of spheres.
    parts.append(glove_palm("GEO_GunnerGlove", (0.38, -0.50, 0.82), glove))
    for finger_index in range(4):
        finger_x = 0.30 + finger_index * 0.052
        finger_z = 0.84 - (finger_index % 2) * 0.012
        parts.append(
            rod_between(
                f"GEO_GunnerGloveFinger_{finger_index}",
                (finger_x, -0.545, finger_z),
                (finger_x + 0.018, -0.655, finger_z - 0.022),
                0.028,
                glove,
            )
        )
    parts.append(rod_between("GEO_GunnerGloveThumb", (0.25, -0.565, 0.755), (0.37, -0.675, 0.735), 0.036, glove))
    # Rifle control details: top rail, rear sight ears, trigger guard, and a
    # small safety lever keep the weapon from reading as a single black bar.
    parts.append(add_cube("GEO_GunnerRifleTopRail", (0.12, -0.50, 0.93), (0.38, 0.055, 0.018), rifle_metal))
    parts.append(add_cube("GEO_GunnerRifleRearSight_L", (-0.18, -0.56, 0.99), (0.018, 0.016, 0.055), rifle_metal))
    parts.append(add_cube("GEO_GunnerRifleRearSight_R", (-0.18, -0.44, 0.99), (0.018, 0.016, 0.055), rifle_metal))
    parts.append(rod_between("GEO_GunnerRifleTriggerGuardFront", (-0.22, -0.56, 0.72), (-0.22, -0.44, 0.72), 0.014, rifle_metal))
    parts.append(rod_between("GEO_GunnerRifleTriggerGuardBottom", (-0.22, -0.56, 0.72), (-0.06, -0.56, 0.72), 0.014, rifle_metal))
    parts.append(rod_between("GEO_GunnerRifleTriggerGuardBack", (-0.06, -0.56, 0.72), (-0.06, -0.44, 0.72), 0.014, rifle_metal))
    parts.append(add_cube("GEO_GunnerRifleSafety", (-0.05, -0.59, 0.86), (0.045, 0.012, 0.018), rifle_metal))

    # Pass21 5-6: weapon furniture and first-person glove articulation cues.
    parts.append(add_cube("GEO_GunnerRifleHandguard", (0.40, -0.50, 0.82), (0.30, 0.085, 0.080), rifle_wood))
    parts.append(add_cube("GEO_GunnerRifleGasBlock", (0.82, -0.50, 0.84), (0.055, 0.060, 0.070), rifle_metal))
    parts.append(add_torus("GEO_GunnerRifleSlingMount_F", 0.040, 0.008, (0.85, -0.50, 0.77), (0.0, math.radians(90.0), 0.0), dark_metal))
    parts.append(add_torus("GEO_GunnerRifleSlingMount_R", 0.040, 0.008, (-0.55, -0.50, 0.74), (0.0, math.radians(90.0), 0.0), dark_metal))
    parts.append(add_cube("GEO_GunnerGloveKnucklePad", (0.36, -0.58, 0.88), (0.105, 0.040, 0.025), glove, rotation=(0.0, math.radians(-8.0), 0.0)))
    parts.append(add_torus("GEO_GunnerGloveCuff", 0.105, 0.020, (0.16, -0.50, 0.79), (0.0, math.radians(90.0), 0.0), glove))

    # The Igla is a separate rear-station weapon state, stowed along the
    # starboard side while the soldier holds the rifle. Gameplay can later
    # attach this assembly to the same rear-weapon socket during weapon swap.
    parts.append(add_cylinder("GEO_IglaLauncherTube", 0.075, 1.36, (-0.46, 0.48, 0.62), (0.0, math.radians(90.0), 0.0), igla_green, vertices=48))
    parts.append(add_cylinder("GEO_IglaFrontCap", 0.105, 0.095, (0.25, 0.48, 0.62), (0.0, math.radians(90.0), 0.0), dark_metal, vertices=40))
    parts.append(add_cylinder("GEO_IglaRearCap", 0.095, 0.080, (-1.18, 0.48, 0.62), (0.0, math.radians(90.0), 0.0), rubber, vertices=40))
    parts.append(add_cube("GEO_IglaGrip", (-0.34, 0.48, 0.49), (0.075, 0.055, 0.14), igla_green, rotation=(0.0, math.radians(-12.0), 0.0)))
    parts.append(add_uv("GEO_IglaBattery", (-0.62, 0.48, 0.50), (0.12, 0.085, 0.105), dark_metal))
    parts.append(add_cube("GEO_IglaSight", (-0.05, 0.48, 0.75), (0.11, 0.045, 0.065), instrument))
    parts.append(add_cube("GEO_IglaShoulderRest", (-1.08, 0.48, 0.55), (0.13, 0.075, 0.10), rubber))
    parts.append(add_torus("GEO_IglaFrontBand", 0.090, 0.012, (0.10, 0.48, 0.62), (0.0, math.radians(90.0), 0.0), dark_metal))

    # Pass21 7: restrained exterior service detail and cowling exhaust vents.
    parts.append(add_cube("GEO_FuselageAccessPanel_L", (1.55, -0.735, 0.28), (0.24, 0.012, 0.16), paint))
    parts.append(add_cube("GEO_FuselageAccessPanel_R", (1.55, 0.735, 0.28), (0.24, 0.012, 0.16), paint))
    parts.append(add_cube("GEO_CowlVent_L", (3.18, -0.64, 0.40), (0.18, 0.018, 0.055), dark_metal, rotation=(0.0, math.radians(-8.0), 0.0)))
    parts.append(add_cube("GEO_CowlVent_R", (3.18, 0.64, 0.40), (0.18, 0.018, 0.055), dark_metal, rotation=(0.0, math.radians(-8.0), 0.0)))

    for side in (-1.0, 1.0):
        for rivet_index, rivet_x in enumerate((-1.70, -1.12, -0.54, 0.04, 0.62, 1.20, 1.78, 2.34)):
            radius_y = 0.56 + 0.16 * max(0.0, 1.0 - abs(rivet_x) / 3.0)
            parts.append(
                add_uv(
                    f"GEO_FuselageRivet_{'L' if side < 0 else 'R'}_{rivet_index}",
                    (rivet_x, side * radius_y, 0.18),
                    (0.024, 0.014, 0.014),
                    dark_metal,
                )
            )
    parts.append(wing_root_fairing("GEO_LeftWingRootFillet", -1.0, paint))
    parts.append(wing_root_fairing("GEO_RightWingRootFillet", 1.0, paint))
    for side in (-1.0, 1.0):
        for fastener_index, fastener_x in enumerate((-0.48, 0.28)):
            parts.append(
                add_uv(
                    f"GEO_WingRootFastener_{'L' if side < 0 else 'R'}_{fastener_index}",
                    (fastener_x, side * 0.79, -0.31),
                    (0.022, 0.014, 0.014),
                    dark_metal,
                )
            )

    # Rounded leading edges, navigation lamps, and a restrained blue/yellow
    # identification treatment break up the previous slab-gray silhouette.
    parts.append(rod_between("GEO_WingLeadingEdge_L", (0.78, 0.0, -0.30), (0.12, -4.52, -0.30), 0.040, paint))
    parts.append(rod_between("GEO_WingLeadingEdge_R", (0.78, 0.0, -0.30), (0.12, 4.52, -0.30), 0.040, paint))
    parts.append(add_uv("GEO_NavLamp_L", (0.08, -4.50, -0.29), (0.075, 0.040, 0.040), nav_red))
    parts.append(add_uv("GEO_NavLamp_R", (0.08, 4.50, -0.29), (0.075, 0.040, 0.040), nav_green))
    for side in (-1.0, 1.0):
        wing_y = side * 2.35
        parts.append(add_cylinder(f"GEO_WingRoundel_{'L' if side < 0 else 'R'}", 0.27, 0.018, (-0.18, wing_y, -0.255), (0.0, 0.0, 0.0), livery_blue, vertices=64))
        parts.append(add_cylinder(f"GEO_WingRoundelCore_{'L' if side < 0 else 'R'}", 0.12, 0.022, (-0.18, wing_y, -0.244), (0.0, 0.0, 0.0), livery_yellow, vertices=64))
    parts.append(add_cube("GEO_LiveryStripe_PortBlue", (0.12, -0.742, 0.26), (0.72, 0.014, 0.055), livery_blue))
    parts.append(add_cube("GEO_LiveryStripe_PortYellow", (-0.62, -0.738, 0.26), (0.28, 0.014, 0.055), livery_yellow))
    parts.append(add_cube("GEO_LiveryStripe_StarboardBlue", (0.12, 0.742, 0.26), (0.72, 0.014, 0.055), livery_blue))
    parts.append(add_cube("GEO_LiveryStripe_StarboardYellow", (-0.62, 0.738, 0.26), (0.28, 0.014, 0.055), livery_yellow))
    parts.append(add_cube("GEO_TailStripeBlue", (-3.06, -0.086, 0.93), (0.14, 0.012, 0.10), livery_blue))
    parts.append(add_cube("GEO_TailStripeYellow", (-2.74, -0.086, 0.93), (0.12, 0.012, 0.10), livery_yellow))

    # Small panel rings and fastener bars add scale cues without turning the
    # fuselage into a continuous dark seam.
    for ring_index, ring_x in enumerate((-1.72, -0.92, -0.12, 0.68, 1.48, 2.20)):
        parts.append(add_torus(f"GEO_FuselagePanelRing_{ring_index}", 0.64, 0.010, (ring_x, 0.0, 0.10), (0.0, math.radians(90.0), 0.0), dark_metal))
    for fastener_index, fastener_x in enumerate((-1.35, -0.68, 0.02, 0.70, 1.38)):
        parts.append(add_uv(f"GEO_PanelFastener_{fastener_index}", (fastener_x, -0.755, 0.38), (0.020, 0.010, 0.020), livery_white))

    # The gunner operates from the port side of the open station.  Apply the
    # same lateral offset to every weapon/arm piece so the rifle does not sit
    # on the aircraft centerline and occlude the seated sightline.
    for obj in parts:
        if obj.name.startswith("GEO_Gunner"):
            obj.location.y -= 0.14

    prop_hub = add_cylinder(
        "GEO_PropHub",
        0.26,
        0.36,
        (3.965, 0.0, 0.0),
        (0.0, math.radians(90.0), 0.0),
        dark_metal,
        vertices=64,
    )
    parts.append(prop_hub)
    parts.append(add_uv("GEO_PropSpinner", (4.01, 0.0, 0.0), (0.125, 0.125, 0.125), dark_metal))
    blade_a = twisted_propeller_pair(
        "GEO_PropBlade_A",
        4.020,
        (
            (0.20, 0.34, 0.085, 31.0),
            (0.38, 0.32, 0.075, 27.0),
            (0.58, 0.28, 0.062, 23.0),
            (0.78, 0.23, 0.050, 18.0),
            (0.96, 0.16, 0.038, 13.0),
            (1.08, 0.07, 0.025, 9.0),
        ),
        dark_metal,
    )
    parts.append(blade_a)

    # Visual landing gear establishes the Yak-52 tricycle stance without
    # entering animation/physics scope.
    for side in (-1.0, 1.0):
        parts.append(
            tapered_oleo_strut(
                f"GEO_MainGearStrut_{'L' if side < 0 else 'R'}",
                (0.28, side * 1.46, -0.20),
                (0.08, side * 1.67, -0.79),
                (0.072, 0.070, 0.058, 0.046, 0.042),
                dark_metal,
            )
        )
        add_wheel(
            f"GEO_MainWheel_{'L' if side < 0 else 'R'}",
            (0.08, side * 1.67, -0.84),
            0.34,
            rubber,
            dark_metal,
        )
        parts.append(add_cylinder(f"GEO_BrakeDisc_{'L' if side < 0 else 'R'}", 0.13, 0.035, (0.08, side * 1.765, -0.84), (math.radians(90.0), 0.0, 0.0), dark_metal, vertices=48))
        parts.append(add_cube(f"GEO_BrakeCaliper_{'L' if side < 0 else 'R'}", (0.18, side * 1.78, -0.76), (0.045, 0.032, 0.12), underside, rotation=(0.0, math.radians(-10.0 * side), 0.0)))
        parts.append(rod_between(f"GEO_TorqueLink_{'L' if side < 0 else 'R'}", (0.03, side * 1.58, -0.65), (0.18, side * 1.66, -0.79), 0.018, dark_metal))
        parts.append(add_cube(f"GEO_GearFairing_{'L' if side < 0 else 'R'}", (0.12, side * 1.55, -0.50), (0.11, 0.08, 0.07), underside, rotation=(0.0, math.radians(-12.0 * side), 0.0)))
        parts.append(
            rod_between(
                f"GEO_GearFork_{'L' if side < 0 else 'R'}",
                (0.14, side * 1.62, -0.68),
                (0.08, side * 1.67, -0.84),
                0.026,
                dark_metal,
                vertices=24,
            )
        )
        gear_door = add_cube(
            f"GEO_GearDoor_{'L' if side < 0 else 'R'}",
            (0.22, side * 1.52, -0.56),
            (0.24, 0.035, 0.10),
            underside,
            rotation=(0.0, math.radians(-12.0), math.radians(4.0 * side)),
        )
        set_origin_world(gear_door, (0.28, side * 1.49, -0.40))
        gear_door["L88_PivotRole"] = "main_gear_door_hinge"
        parts.append(gear_door)
    parts.append(
        tapered_oleo_strut(
            "GEO_NoseGearStrut",
            (2.28, 0.0, -0.18),
            (2.38, 0.0, -0.80),
            (0.064, 0.062, 0.052, 0.042, 0.038),
            dark_metal,
        )
    )
    add_wheel("GEO_NoseWheel", (2.38, 0.0, -0.86), 0.27, rubber, dark_metal)
    parts.append(add_cylinder("GEO_NoseBrakeDisc", 0.10, 0.030, (2.38, 0.0, -0.86), (math.radians(90.0), 0.0, 0.0), dark_metal, vertices=48))
    parts.append(add_cube("GEO_NoseBrakeCaliper", (2.43, -0.15, -0.79), (0.035, 0.025, 0.08), underside))
    parts.append(rod_between("GEO_NoseGearFork", (2.34, 0.0, -0.67), (2.38, 0.0, -0.86), 0.024, dark_metal, vertices=24))
    nose_gear_door = add_cube("GEO_NoseGearDoor", (2.30, -0.20, -0.54), (0.22, 0.035, 0.095), underside, rotation=(0.0, math.radians(8.0), 0.0))
    set_origin_world(nose_gear_door, (2.25, -0.18, -0.36))
    nose_gear_door["L88_PivotRole"] = "nose_gear_door_hinge"
    parts.append(nose_gear_door)

    for obj in list(bpy.context.scene.objects):
        if obj == root or obj.parent is not None or obj.type in {"LIGHT", "CAMERA"}:
            continue
        matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = matrix
    return root


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    configure_scene()
    root = build_aircraft()
    bpy.context.view_layer.update()

    hero_objects = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.name.startswith("GEO_")
    ]
    semantic_report = apply_l88_semantic_pbr_uv_layers(hero_objects)
    for obj in hero_objects:
        smooth_mesh(obj, weighted=True)
    minimum, maximum = world_bounds(hero_objects)
    dimensions = maximum - minimum

    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in hero_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(EXPORT),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )
    markers = build_l88_rear_weapon_ads_markers(root)
    bpy.ops.wm.save_as_mainfile(filepath=str(MASTER_BLEND))
    MARKER_REPORT.parent.mkdir(parents=True, exist_ok=True)
    MARKER_REPORT.write_text(
        json.dumps(
            {
                "source": str(MASTER_BLEND),
                "marker_count": len(markers),
                "markers": [
                    {
                        "name": marker.name,
                        "role": marker.get("L88_MarkerRole"),
                        "location_m": [round(float(value), 6) for value in marker.location],
                        "forward": [1.0, 0.0, 0.0],
                    }
                    for marker in markers
                ],
                "render_mesh_excluded": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    floor_z = minimum.z - 0.04
    bpy.ops.mesh.primitive_plane_add(size=34.0, location=(0.0, 0.0, floor_z))
    floor = bpy.context.object
    floor.name = "L88_StudioFloor"
    floor.data.materials.append(material("M_L88_Floor", (0.08, 0.10, 0.13), 0.0, 0.66))

    target = Vector((0.0, 0.0, 0.0))
    add_area("L88_Key", (7.0, -7.0, 8.0), 880.0, 6.0, (1.0, 0.76, 0.55), target)
    add_area("L88_Fill", (-4.0, 5.0, 5.0), 680.0, 7.0, (0.48, 0.68, 1.0), target)
    add_area("L88_Rim", (-5.0, -4.0, 7.0), 720.0, 5.0, (0.75, 0.86, 1.0), target)
    add_area("L88_CockpitFill", (-1.2, -2.2, 2.8), 420.0, 3.5, (0.58, 0.72, 1.0), (0.0, -0.25, 0.72))

    specs = (
        ("SideOrtho", (0.0, -15.0, 0.4), target, True, 10.8),
        ("FrontOrtho", (15.0, 0.0, 0.2), target, True, 10.8),
        ("TopOrtho", (0.0, 0.0, 15.0), target, True, 10.8),
        ("Beauty", (11.5, -11.5, 6.7), (0.0, 0.0, -0.05), False, 12.0),
        # Place the validation eye point in front of the rear seat back, not
        # behind it; this is the gunner's seated viewpoint looking toward the
        # pilot's panel through the open station.
        # Seated eye point is inside the open rear station, just port of the
        # centerline.  Putting the camera outside the rail turns the frame
        # into a foreground cage and hides the hand/weapon context.
        # The gunner's natural seated view is port-side, out through the open
        # station.  Keeping this eye point on the port rim makes the rifle and
        # hand part of the gameplay sightline instead of a forward-facing rail
        # cage.
        ("RearCockpitHero", (-1.20, -1.10, 1.10), (0.30, -0.55, 0.68), False, 4.2),
        # Companion weapon-arc proof from the port side. This makes the rifle,
        # mount, glove, and open-cockpit relationship independently judgeable.
        ("RearGunnerWeaponHero", (-0.72, -1.15, 1.04), (0.78, -0.64, 0.80), False, 4.2),
        # Dedicated iron-sight proof aligned with the port-side barrel.  This
        # is a validation still, not a gameplay camera replacement.
        ("RearGunnerADS", (-0.90, -0.64, 1.02), (1.58, -0.64, 1.00), False, 3.2),
        # Exterior cockpit proof for station scale, seat/harness, and open
        # canopy mechanics; this is separate from the seated eye-point frame.
        ("RearCockpitExterior", (-1.45, -2.70, 1.55), (0.15, -0.20, 0.48), False, 5.4),
        # Pass20 inspection camera: hide the detachable weapon overlay and
        # inspect the new throttle, trim, switches, radio, latches, wiring, and
        # harness hardware without changing the exported gameplay hierarchy.
        ("RearCockpitControls", (-1.25, -1.75, 1.42), (0.08, 0.0, 0.48), False, 4.4),
    )
    renders = []
    for name, location, aim, ortho, scale in specs:
        camera = add_camera(
            "AAA_Cam_L88_" + name,
            location,
            aim,
            46.0 if name == "RearGunnerADS" else (38.0 if name == "RearCockpitHero" else (40.0 if name == "RearGunnerWeaponHero" else (45.0 if name in ("RearCockpitExterior", "RearCockpitControls") else 58.0))),
            orthographic=ortho,
            scale=scale,
        )
        bpy.context.scene.camera = camera
        hidden_for_hero = []
        if name in ("RearCockpitHero", "RearGunnerWeaponHero", "RearGunnerADS", "RearCockpitExterior", "RearCockpitControls"):
            # The hero gate evaluates the open rear gunner station. Keep the
            # canopy in the exported GLB, but temporarily remove the opaque
            # validation proxy so the still proves that the interior exists.
            canopy_proxy = bpy.data.objects.get("GEO_FrontCanopyGlass")
            if canopy_proxy is not None:
                hidden_for_hero.append((canopy_proxy, canopy_proxy.hide_render))
                canopy_proxy.hide_render = True
        if name == "RearGunnerADS":
            # Isolate the sight picture for validation.  The canopy hardware
            # remains in the exported GLB; this camera proves the authored
            # rear aperture/front post relationship without a rail clipping
            # through the reticle.
            for obj in bpy.data.objects:
                if obj.name.startswith("GEO_Canopy"):
                    hidden_for_hero.append((obj, obj.hide_render))
                    obj.hide_render = True
        if name == "RearCockpitControls":
            for obj in bpy.data.objects:
                if obj.name.startswith("GEO_Gunner"):
                    hidden_for_hero.append((obj, obj.hide_render))
                    obj.hide_render = True
        output = OUT_DIR / f"AAA_Cam_L88_{name}_FINAL.png"
        bpy.context.scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        for hidden_obj, previous in hidden_for_hero:
            hidden_obj.hide_render = previous
        renders.append({"camera": name, "path": str(output), "bytes": output.stat().st_size})

    report = {
        "target_dimensions_m": [TARGET_LENGTH, TARGET_SPAN, TARGET_HEIGHT],
        "measured_bounds_min_m": list(minimum),
        "measured_bounds_max_m": list(maximum),
        "measured_dimensions_m": list(dimensions),
        "dimension_error_percent": [
            100.0 * (dimensions.x - TARGET_LENGTH) / TARGET_LENGTH,
            100.0 * (dimensions.y - TARGET_SPAN) / TARGET_SPAN,
            100.0 * (dimensions.z - TARGET_HEIGHT) / TARGET_HEIGHT,
        ],
        "hero_mesh_objects": len(hero_objects),
        "semantic_material_families": semantic_report["family_counts"],
        "uv_layer_name": semantic_report["uv_layer"],
        "uv_layer_mesh_count": semantic_report["mesh_count"],
        "marker_report": str(MARKER_REPORT),
        "marker_count": len(markers),
        "export": str(EXPORT),
        "master_blend": str(MASTER_BLEND),
        "renders": renders,
        "gate": "silhouette_blockout_not_visual_promotion",
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("[SkyguardAAA] L88 Yak-52 silhouette blockout complete")
    print(json.dumps(report))


main()
