import ast
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock


# Define mock classes for Blender modules if running outside Blender
class MockVector(tuple):
    def __new__(cls, coords=(0.0, 0.0, 0.0)):
        return super().__new__(cls, tuple(coords))

    @property
    def length(self):
        return sum(x ** 2 for x in self) ** 0.5

    def __sub__(self, other):
        return MockVector(a - b for a, b in zip(self, other))

    def __add__(self, other):
        return MockVector(a + b for a, b in zip(self, other))

    def __truediv__(self, scalar):
        return MockVector(a / scalar for a in self)

    def to_track_quat(self, track='Z', up='Y'):
        return (1.0, 0.0, 0.0, 0.0)


class MockEuler(tuple):
    def __new__(cls, angles=(0.0, 0.0, 0.0)):
        return super().__new__(cls, tuple(angles))


def setup_blender_mocks():
    if "bpy" not in sys.modules:
        mock_bpy = MagicMock()

        # Setup data collections
        mock_bpy.data.collections.new = lambda name: MagicMock(name=name, objects=MagicMock())
        mock_bpy.data.materials.new = lambda name: MagicMock(name=name, node_tree=MagicMock(nodes={}))
        mock_bpy.data.lights.new = lambda name, type: MagicMock(name=name, type=type)
        mock_bpy.data.cameras.new = lambda name: MagicMock(name=name)
        mock_bpy.data.objects.new = lambda name, data: MagicMock(name=name, data=data)

        # Setup context and scene
        mock_obj = MagicMock()
        mock_obj.name = "MockObject"
        mock_obj.modifiers = MagicMock()
        mock_obj.modifiers.new = lambda name, type: MagicMock(name=name, type=type)
        mock_obj.data = MagicMock(materials=[], polygons=[MagicMock()])
        mock_obj.users_collection = []
        mock_obj.get = lambda key, default=None: default

        mock_bpy.context.object = mock_obj
        mock_bpy.context.scene.collection.children.link = MagicMock()
        mock_bpy.path.abspath = lambda p: p.replace("//", "./")

        sys.modules["bpy"] = mock_bpy

    if "mathutils" not in sys.modules:
        mock_mathutils = MagicMock()
        mock_mathutils.Vector = MockVector
        mock_mathutils.Euler = MockEuler
        sys.modules["mathutils"] = mock_mathutils


setup_blender_mocks()

# Now import procedural_forge
import procedural_forge


class TestProceduralForge(unittest.TestCase):

    def test_python_syntax(self):
        """Verifies that procedural_forge.py has valid Python syntax via AST parsing."""
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "procedural_forge.py"
        )
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        self.assertIsNotNone(tree)

    def test_config_defaults(self):
        """Validates default CONFIG parameters."""
        config = procedural_forge.CONFIG
        self.assertIn("seed", config)
        self.assertIn("complexity", config)
        self.assertIn("detail_density", config)
        self.assertIn("enable_lod", config)
        self.assertIn("enable_metadata", config)
        self.assertEqual(config["object_type"], "SCIFI_REACTOR")

    def test_seed_system(self):
        """Tests deterministic seed generation and string hashing."""
        seed1 = procedural_forge.seed_from_string("REACTOR_ALPHA")
        seed2 = procedural_forge.seed_from_string("REACTOR_ALPHA")
        seed3 = procedural_forge.seed_from_string("REACTOR_BETA")

        self.assertEqual(seed1, seed2)
        self.assertNotEqual(seed1, seed3)

        procedural_forge.set_seed(12345)
        self.assertEqual(procedural_forge.CONFIG["seed"], 12345)
        self.assertEqual(procedural_forge.METADATA["seed"], 12345)

    def test_random_helpers(self):
        """Tests random helper bounds and vector generation."""
        procedural_forge.set_seed(42)

        val = procedural_forge.rand(10, 20)
        self.assertTrue(10 <= val <= 20)

        ival = procedural_forge.randi(1, 5)
        self.assertTrue(1 <= ival <= 5)

        color = procedural_forge.random_color()
        self.assertEqual(len(color), 3)
        for c in color:
            self.assertTrue(0.0 <= c <= 1.0)

        vec = procedural_forge.random_vector(scale=2.0)
        self.assertEqual(len(vec), 3)

    def test_object_registration(self):
        """Tests register_object updates global objects and metadata lists."""
        procedural_forge.GENERATED_OBJECTS.clear()
        procedural_forge.METADATA["objects"].clear()

        mock_obj = dict(name="TestReactorObj")
        # dict as object with item access
        mock_obj["name"] = "TestReactorObj"

        class MockObject(dict):
            name = "TestReactorObj"

        obj_instance = MockObject()

        registered = procedural_forge.register_object(obj_instance, category="reactor")

        self.assertEqual(len(procedural_forge.GENERATED_OBJECTS), 1)
        self.assertEqual(registered["PF_CATEGORY"], "reactor")
        self.assertEqual(len(procedural_forge.METADATA["objects"]), 1)
        self.assertEqual(procedural_forge.METADATA["objects"][0]["name"], "TestReactorObj")

    def test_material_library(self):
        """Tests material creation library initialization."""
        procedural_forge.create_material_library()
        mats = procedural_forge.MATERIALS
        self.assertIn("MAT_BLACK_METAL", mats)
        self.assertIn("MAT_STEEL", mats)
        self.assertIn("MAT_ENERGY_BLUE", mats)

    def test_metadata_export(self):
        """Tests export_metadata output file format and content."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            procedural_forge.set_seed(999)
            procedural_forge.CONFIG["enable_metadata"] = True
            procedural_forge.GENERATED_OBJECTS.clear()

            procedural_forge.export_metadata(tmp_dir)

            expected_file = os.path.join(tmp_dir, "metadata_seed_999.json")
            self.assertTrue(os.path.exists(expected_file))

            with open(expected_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data["seed"], 999)
            self.assertEqual(data["generator"], "Procedural Forge X")


if __name__ == "__main__":
    unittest.main()
