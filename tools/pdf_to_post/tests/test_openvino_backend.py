from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

from pdf_to_post.hybrid import HybridError
from pdf_to_post.openvino_backend import (
    DETECTION_MODEL,
    RECOGNITION_MODEL,
    configure_openvino_gpu_fp32,
)


class FakeModel:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.inputs = ("x",)
        self.shape: tuple[int, ...] | None = None

    def reshape(self, shapes: dict[str, tuple[int, ...]]) -> None:
        self.shape = next(iter(shapes.values()))


class FakeCompiledModel:
    def __init__(self, output: object, device: str) -> None:
        self.output = output
        self.device = device
        self.inputs: list[object] = []

    def create_infer_request(self) -> "FakeCompiledModel":
        return self

    def infer(self, inputs: list[object]) -> dict[str, object]:
        self.inputs = inputs
        return {"output": self.output}

    def get_property(self, name: str) -> object:
        if name == "EXECUTION_DEVICES":
            return [f"{self.device}.0"]
        if name == "INFERENCE_PRECISION_HINT":
            return "float32"
        raise KeyError(name)


class FakeCore:
    def __init__(self, devices: list[str]) -> None:
        self.available_devices = devices
        self.compiled: list[
            tuple[FakeModel, str, dict[str, str], FakeCompiledModel]
        ] = []

    def read_model(self, path: Path) -> FakeModel:
        return FakeModel(path)

    def compile_model(
        self, model: FakeModel, device: str, config: dict[str, str]
    ) -> FakeCompiledModel:
        compiled = FakeCompiledModel(model.path.name, device)
        self.compiled.append((model, device, config, compiled))
        return compiled


def make_pipeline() -> SimpleNamespace:
    inner = SimpleNamespace(
        text_det_model=SimpleNamespace(runner=None),
        text_rec_model=SimpleNamespace(runner=None),
    )
    return SimpleNamespace(paddlex_pipeline=SimpleNamespace(_pipeline=inner))


class OpenVINOBackendTest(unittest.TestCase):
    def create_models(self, work_dir: Path) -> None:
        model_dir = work_dir / "cache" / "openvino" / "models"
        model_dir.mkdir(parents=True)
        (model_dir / f"{DETECTION_MODEL}.onnx").write_bytes(b"det")
        (model_dir / f"{RECOGNITION_MODEL}.onnx").write_bytes(b"rec")

    def test_configures_static_detection_gpu_and_recognition_cpu(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory)
            self.create_models(work_dir)
            core = FakeCore(["CPU", "GPU"])
            pipeline = make_pipeline()
            module = SimpleNamespace(Core=lambda: core)

            with patch.dict(sys.modules, {"openvino": module}):
                configure_openvino_gpu_fp32(pipeline, work_dir)

            inner = pipeline.paddlex_pipeline._pipeline
            tensor = SimpleNamespace(shape=(1, 3, 1504, 1984))
            self.assertEqual(
                inner.text_det_model.runner(x=[tensor]),
                [f"{DETECTION_MODEL}.onnx"],
            )
            self.assertEqual(
                inner.text_rec_model.runner(x=[tensor]),
                [f"{RECOGNITION_MODEL}.onnx"],
            )
            self.assertEqual([item[1] for item in core.compiled], ["CPU", "GPU"])
            self.assertEqual(core.compiled[1][0].shape, tensor.shape)
            inner.text_det_model.runner(x=[tensor])
            self.assertEqual(len(core.compiled), 2)
            resized = SimpleNamespace(shape=(1, 3, 960, 1280))
            inner.text_det_model.runner(x=[resized])
            self.assertEqual(len(core.compiled), 3)
            for _, _, config, _ in core.compiled:
                self.assertEqual(config["INFERENCE_PRECISION_HINT"], "f32")
                self.assertEqual(config["PERFORMANCE_HINT"], "LATENCY")
            self.assertEqual(core.compiled[1][2]["NUM_STREAMS"], "1")

    def test_rejects_environment_without_gpu(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory)
            self.create_models(work_dir)
            module = SimpleNamespace(Core=lambda: FakeCore(["CPU"]))

            with patch.dict(sys.modules, {"openvino": module}):
                with self.assertRaisesRegex(HybridError, "Intel GPU"):
                    configure_openvino_gpu_fp32(make_pipeline(), work_dir)

    def test_reports_missing_onnx_models(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(HybridError, "ONNX 모델"):
                configure_openvino_gpu_fp32(make_pipeline(), Path(directory))


if __name__ == "__main__":
    unittest.main()
