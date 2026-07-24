from __future__ import annotations

from pathlib import Path
from typing import Any

from pdf_to_post.hybrid import HybridError


DETECTION_MODEL = "PP-OCRv5_server_det"
RECOGNITION_MODEL = "korean_PP-OCRv5_mobile_rec"


class _OpenVINORunner:
    def __init__(self, compiled_model: Any, model_name: str) -> None:
        self.compiled_model = compiled_model
        self.model_name = model_name
        self.request = compiled_model.create_infer_request()

    def __call__(self, **kwargs: Any) -> list[Any]:
        value = next(iter(kwargs.values()))
        tensor = value[0] if isinstance(value, (list, tuple)) else value
        try:
            outputs = self.request.infer([tensor])
        except Exception as error:
            raise RuntimeError(
                f"OpenVINO {self.model_name} 추론 실패: {error}"
            ) from error
        copied = [
            output.copy() if hasattr(output, "copy") else output
            for output in outputs.values()
        ]
        del outputs
        return copied


class _StaticShapeOpenVINORunner:
    def __init__(
        self,
        core: Any,
        model_path: Path,
        model_name: str,
        config: dict[str, str],
    ) -> None:
        self.core = core
        self.model_path = model_path
        self.model_name = model_name
        self.config = config
        self.shape: tuple[int, ...] | None = None
        self.runner: _OpenVINORunner | None = None

    def __call__(self, **kwargs: Any) -> list[Any]:
        value = next(iter(kwargs.values()))
        tensor = value[0] if isinstance(value, (list, tuple)) else value
        shape = tuple(int(dimension) for dimension in tensor.shape)
        if self.runner is None or shape != self.shape:
            model = self.core.read_model(self.model_path)
            model.reshape({model.inputs[0]: shape})
            compiled = self.core.compile_model(model, "GPU", self.config)
            _validate_compiled_model(compiled, self.model_name, "GPU")
            self.runner = _OpenVINORunner(compiled, self.model_name)
            self.shape = shape
        return self.runner(**kwargs)


def _validate_compiled_model(
    compiled_model: Any, model_name: str, expected_device: str
) -> None:
    devices = compiled_model.get_property("EXECUTION_DEVICES")
    if not any(str(device).startswith(expected_device) for device in devices):
        raise HybridError(
            f"OpenVINO {model_name} 모델이 {expected_device}에 배치되지 않았습니다: "
            f"{devices}"
        )
    precision = str(compiled_model.get_property("INFERENCE_PRECISION_HINT"))
    if "float32" not in precision:
        raise HybridError(
            f"OpenVINO {model_name} 모델의 FP32 강제 설정이 적용되지 않았습니다: "
            f"{precision}"
        )


def configure_openvino_gpu_fp32(pipeline: Any, work_dir: Path) -> None:
    model_dir = work_dir / "cache" / "openvino" / "models"
    detection_path = model_dir / f"{DETECTION_MODEL}.onnx"
    recognition_path = model_dir / f"{RECOGNITION_MODEL}.onnx"
    missing = [
        path for path in (detection_path, recognition_path) if not path.is_file()
    ]
    if missing:
        paths = ", ".join(str(path) for path in missing)
        raise HybridError(
            "OpenVINO용 ONNX 모델을 찾을 수 없습니다. README의 "
            f"'OpenVINO 준비' 절에 따라 변환하세요: {paths}"
        )

    try:
        import openvino as ov
    except ModuleNotFoundError as error:
        raise HybridError(
            "OpenVINO가 설치되어 있지 않습니다. "
            "`pip install -e \"tools/pdf_to_post[paddle,openvino]\"`를 실행하세요."
        ) from error

    try:
        detection_config = {
            "INFERENCE_PRECISION_HINT": "f32",
            "NUM_STREAMS": "1",
            "PERFORMANCE_HINT": "LATENCY",
        }
        recognition_config = {
            "INFERENCE_PRECISION_HINT": "f32",
            "PERFORMANCE_HINT": "LATENCY",
        }
        core = ov.Core()
        if not any(str(device).startswith("GPU") for device in core.available_devices):
            raise HybridError(
                "OpenVINO에서 Intel GPU를 찾지 못했습니다. "
                f"감지된 장치: {core.available_devices}"
            )
        recognition = core.compile_model(
            core.read_model(recognition_path), "CPU", recognition_config
        )
        _validate_compiled_model(recognition, RECOGNITION_MODEL, "CPU")
        inner = pipeline.paddlex_pipeline._pipeline
        inner.text_det_model.runner = _StaticShapeOpenVINORunner(
            core,
            detection_path,
            DETECTION_MODEL,
            detection_config,
        )
        inner.text_rec_model.runner = _OpenVINORunner(recognition, RECOGNITION_MODEL)
    except HybridError:
        raise
    except Exception as error:
        raise HybridError(
            f"OpenVINO GPU FP32 모델 초기화에 실패했습니다: {error}"
        ) from error
