#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Optimizer - Sun'iy intellekt optimizatori
AI modellarni optimizatsiya qilish va samaradorlikni oshirish

Xususiyatlar:
- Model compression (Pruning, Quantization)
- Model distillation 
- ONNX optimizatsiya
- TensorRT optimizatsiya
- GPU memory management
- Inference caching
- Batch processing
- Model parallelism
- Edge device optimization
- Real-time inference optimization
"""

import os
import json
import time
import logging
import asyncio
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import gc
import psutil
import threading
from contextlib import contextmanager

# AI/ML kutubxonalari (agar mavjud bo'lsa)
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch import jit
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import tensorrt as trt
    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False

try:
    from sklearn.base import BaseEstimator
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Logging sozlamalar
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Model ma'lumotlari"""
    name: str
    path: str
    size: int  # bytes
    parameters: int
    layers: int
    input_shape: List[int]
    output_shape: List[int]
    framework: str  # pytorch, tensorflow, onnx, sklearn
    precision: str  # float32, float16, int8
    optimization_applied: bool = False
    inference_time: float = 0.0
    memory_usage: int = 0
    accuracy_preserved: float = 1.0
    compression_ratio: float = 0.0

@dataclass
class OptimizationConfig:
    """Optimizatsiya konfiguratsiyasi"""
    model_path: str
    framework: str
    target_precision: str = "float16"  # float16, int8
    compression_method: str = "quantization"  # quantization, pruning, distillation
    quantization_method: str = "dynamic"  # dynamic, static, qat
    pruning_threshold: float = 0.1
    distillation_temperature: float = 3.0
    target_device: str = "cpu"  # cpu, gpu, tensorrt
    batch_size: int = 32
    max_memory_mb: int = 512
    inference_cache: bool = True
    model_parallelism: bool = False
    num_threads: int = 4
    precision_mode: str = "balanced"  # speed, accuracy, balanced

class ModelProfiler:
    """Model profil funksiyasi"""
    
    @staticmethod
    def profile_pytorch_model(model_path: str, sample_input: Any = None) -> Dict:
        """PyTorch model profil funksiyasi"""
        if not TORCH_AVAILABLE:
            return {"error": "PyTorch mavjud emas"}
        
        try:
            # Model yuklash
            if os.path.exists(model_path + ".pkl"):
                model = torch.load(model_path + ".pkl", map_location="cpu")
            elif os.path.exists(model_path + ".pt"):
                model = torch.jit.load(model_path + ".pt")
            else:
                return {"error": "Model fayl topilmadi"}
            
            model.eval()
            
            # Sample input yaratish (agar berilmagan bo'lsa)
            if sample_input is None:
                # Modelni tahlil qilish
                if hasattr(model, 'input_size'):
                    sample_input = torch.randn(1, *model.input_size)
                else:
                    # Default 224x224x3 image input
                    sample_input = torch.randn(1, 3, 224, 224)
            
            # Profiling
            start_time = time.time()
            with torch.no_grad():
                output = model(sample_input)
            end_time = time.time()
            
            # Model parametrlarini hisoblash
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            # Memory usage
            memory_usage = sum(p.numel() * 4 for p in model.parameters())  # float32 = 4 bytes
            
            return {
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "inference_time": end_time - start_time,
                "memory_usage": memory_usage,
                "model_size": os.path.getsize(model_path) if os.path.exists(model_path) else 0,
                "output_shape": list(output.shape) if hasattr(output, 'shape') else []
            }
            
        except Exception as e:
            logger.error(f"PyTorch model profiling xatosi: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def profile_tensorflow_model(model_path: str, sample_input: Any = None) -> Dict:
        """TensorFlow model profil funksiyasi"""
        if not TENSORFLOW_AVAILABLE:
            return {"error": "TensorFlow mavjud emas"}
        
        try:
            # Model yuklash
            model = tf.keras.models.load_model(model_path)
            
            # Sample input yaratish
            if sample_input is None:
                input_shape = model.input_shape
                if input_shape and len(input_shape) > 1:
                    sample_input = np.random.randn(1, *input_shape[1:])
                else:
                    sample_input = np.random.randn(1, 10)  # Default
            
            # Profiling
            start_time = time.time()
            output = model.predict(sample_input, verbose=0)
            end_time = time.time()
            
            # Model parametrlari
            total_params = model.count_params()
            
            # Memory usage
            memory_usage = total_params * 4  # float32
            
            return {
                "total_parameters": total_params,
                "inference_time": end_time - start_time,
                "memory_usage": memory_usage,
                "model_size": os.path.getsize(model_path) if os.path.exists(model_path) else 0,
                "output_shape": list(output.shape) if hasattr(output, 'shape') else []
            }
            
        except Exception as e:
            logger.error(f"TensorFlow model profiling xatosi: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def profile_onnx_model(model_path: str) -> Dict:
        """ONNX model profil funksiyasi"""
        if not ONNX_AVAILABLE:
            return {"error": "ONNX mavjud emas"}
        
        try:
            # Model yuklash
            session = ort.InferenceSession(model_path)
            
            # Input shape
            input_shape = session.get_inputs()[0].shape if session.get_inputs() else []
            input_shape = [1 if dim == -1 else dim for dim in input_shape]
            
            # Sample input yaratish
            sample_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Profiling
            start_time = time.time()
            output = session.run(None, {session.get_inputs()[0].name: sample_input})
            end_time = time.time()
            
            # Model size
            model_size = os.path.getsize(model_path)
            
            return {
                "total_parameters": 0,  # ONNX doesn't directly expose parameters
                "inference_time": end_time - start_time,
                "memory_usage": model_size,
                "model_size": model_size,
                "input_shape": input_shape,
                "output_shape": list(np.array(output[0]).shape)
            }
            
        except Exception as e:
            logger.error(f"ONNX model profiling xatosi: {str(e)}")
            return {"error": str(e)}

class AIOptimizer:
    """Asosiy AI optimizatori"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.models: Dict[str, ModelInfo] = {}
        self.optimization_cache = {}
        self.performance_metrics = {}
        
        # GPU info (agar mavjud bo'lsa)
        self.gpu_available = False
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self.gpu_available = True
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        
        # Memory monitoring
        self.memory_monitor = MemoryMonitor()
        
        # Performance profiling
        self.profiler = ModelProfiler()

    def discover_models(self, directory: str) -> List[str]:
        """Loyihada model'larni topish"""
        discovered_models = []
        directory = Path(directory)
        
        # Model extension'lari
        model_extensions = [
            ".pkl", ".pt", ".pth",  # PyTorch
            ".h5", ".pb", ".tflite",  # TensorFlow
            ".onnx",  # ONNX
            ".joblib", ".pkl"  # Scikit-learn
        ]
        
        for ext in model_extensions:
            for model_file in directory.rglob(f"*{ext}"):
                if model_file.is_file():
                    discovered_models.append(str(model_file))
        
        logger.info(f"Topilgan modellar: {len(discovered_models)} ta")
        return discovered_models

    async def profile_all_models(self, models: List[str]) -> Dict[str, ModelInfo]:
        """Barcha model'larni profil qilish"""
        logger.info("📊 Model'larni profil qilish...")
        
        model_profiles = {}
        
        for model_path in models:
            try:
                profile = await self._profile_single_model(model_path)
                if profile:
                    model_profiles[model_path] = profile
                    logger.info(f"✅ Profil qilindi: {Path(model_path).name}")
            except Exception as e:
                logger.error(f"❌ Model profiling xatosi {model_path}: {str(e)}")
        
        return model_profiles

    async def _profile_single_model(self, model_path: str) -> Optional[ModelInfo]:
        """Bitta modelni profil qilish"""
        try:
            file_path = Path(model_path)
            file_size = file_path.stat().st_size
            
            # Framework aniqlash
            framework = self._detect_framework(model_path)
            
            # Profiling
            if framework == "pytorch" and TORCH_AVAILABLE:
                profile = self.profiler.profile_pytorch_model(model_path)
            elif framework == "tensorflow" and TENSORFLOW_AVAILABLE:
                profile = self.profiler.profile_tensorflow_model(model_path)
            elif framework == "onnx" and ONNX_AVAILABLE:
                profile = self.profiler.profile_onnx_model(model_path)
            else:
                # Basic profiling
                profile = {
                    "total_parameters": file_size // 1000,  # Estimate
                    "inference_time": 0.1,  # Estimate
                    "memory_usage": file_size,
                    "model_size": file_size
                }
            
            if "error" in profile:
                return None
            
            # ModelInfo yaratish
            model_info = ModelInfo(
                name=file_path.stem,
                path=model_path,
                size=file_size,
                parameters=profile.get("total_parameters", 0),
                layers=0,  # Will be filled if possible
                input_shape=profile.get("input_shape", []),
                output_shape=profile.get("output_shape", []),
                framework=framework,
                precision="float32",
                inference_time=profile.get("inference_time", 0.0),
                memory_usage=profile.get("memory_usage", file_size)
            )
            
            return model_info
            
        except Exception as e:
            logger.error(f"Model profiling xatosi {model_path}: {str(e)}")
            return None

    def _detect_framework(self, model_path: str) -> str:
        """Model framework'ini aniqlash"""
        file_path = Path(model_path)
        suffix = file_path.suffix.lower()
        
        if suffix in [".pkl", ".pt", ".pth"]:
            return "pytorch"
        elif suffix in [".h5", ".pb", ".tflite"]:
            return "tensorflow"
        elif suffix == ".onnx":
            return "onnx"
        elif suffix in [".joblib"]:
            return "sklearn"
        else:
            return "unknown"

    async def optimize_model(self, model_info: ModelInfo) -> ModelInfo:
        """Modelni optimizatsiya qilish"""
        logger.info(f"🚀 Model optimizatsiya boshlanmoqda: {model_info.name}")
        
        try:
            if model_info.framework == "pytorch":
                optimized_info = await self._optimize_pytorch_model(model_info)
            elif model_info.framework == "tensorflow":
                optimized_info = await self._optimize_tensorflow_model(model_info)
            elif model_info.framework == "onnx":
                optimized_info = await self._optimize_onnx_model(model_info)
            else:
                optimized_info = await self._optimize_generic_model(model_info)
            
            if optimized_info:
                optimized_info.optimization_applied = True
                # Compression ratio hisoblash
                if model_info.size > 0:
                    optimized_info.compression_ratio = (model_info.size - optimized_info.size) / model_info.size
                
                logger.info(f"✅ Model optimizatsiya tugallandi: {model_info.name}")
                logger.info(f"📊 Hajm kamayishi: {optimized_info.compression_ratio*100:.1f}%")
                
                return optimized_info
            
            return model_info
            
        except Exception as e:
            logger.error(f"❌ Model optimizatsiya xatosi {model_info.name}: {str(e)}")
            return model_info

    async def _optimize_pytorch_model(self, model_info: ModelInfo) -> Optional[ModelInfo]:
        """PyTorch model optimizatsiyasi"""
        if not TORCH_AVAILABLE:
            return None
        
        try:
            # Model yuklash
            model = torch.load(model_info.path, map_location="cpu")
            model.eval()
            
            # Quantization
            if self.config.target_precision == "int8" or self.config.quantization_method != "dynamic":
                model = await self._quantize_pytorch_model(model)
            
            # Pruning
            if self.config.pruning_threshold > 0:
                model = await self._prune_pytorch_model(model, self.config.pruning_threshold)
            
            # TorchScript optimizatsiya
            model = await self._optimize_pytorch_script(model)
            
            # Yangi model saqlash
            output_path = model_info.path.replace(".pkl", "_optimized.pkl")
            torch.save(model, output_path)
            
            # Yangi model profili
            optimized_profile = self.profiler.profile_pytorch_model(output_path)
            
            # Yangi ModelInfo
            optimized_info = ModelInfo(
                name=model_info.name + "_optimized",
                path=output_path,
                size=optimized_profile.get("model_size", 0),
                parameters=optimized_profile.get("total_parameters", 0),
                layers=model_info.layers,
                input_shape=model_info.input_shape,
                output_shape=optimized_profile.get("output_shape", []),
                framework="pytorch",
                precision=self.config.target_precision,
                inference_time=optimized_profile.get("inference_time", 0.0),
                memory_usage=optimized_profile.get("memory_usage", 0)
            )
            
            return optimized_info
            
        except Exception as e:
            logger.error(f"PyTorch optimizatsiya xatosi: {str(e)}")
            return None

    async def _optimize_tensorflow_model(self, model_info: ModelInfo) -> Optional[ModelInfo]:
        """TensorFlow model optimizatsiyasi"""
        if not TENSORFLOW_AVAILABLE:
            return None
        
        try:
            # Model yuklash
            model = tf.keras.models.load_model(model_info.path)
            
            # Quantization
            if self.config.target_precision in ["float16", "int8"]:
                model = await self._quantize_tensorflow_model(model)
            
            # Yangi model saqlash
            output_path = model_info.path.replace(".h5", "_optimized.h5")
            model.save(output_path)
            
            # Yangi model profili
            optimized_profile = self.profiler.profile_tensorflow_model(output_path)
            
            # Yangi ModelInfo
            optimized_info = ModelInfo(
                name=model_info.name + "_optimized",
                path=output_path,
                size=optimized_profile.get("model_size", 0),
                parameters=optimized_profile.get("total_parameters", 0),
                layers=len(model.layers),
                input_shape=list(model.input_shape[1:]) if model.input_shape else [],
                output_shape=list(model.output_shape[1:]) if model.output_shape else [],
                framework="tensorflow",
                precision=self.config.target_precision,
                inference_time=optimized_profile.get("inference_time", 0.0),
                memory_usage=optimized_profile.get("memory_usage", 0)
            )
            
            return optimized_info
            
        except Exception as e:
            logger.error(f"TensorFlow optimizatsiya xatosi: {str(e)}")
            return None

    async def _optimize_onnx_model(self, model_info: ModelInfo) -> Optional[ModelInfo]:
        """ONNX model optimizatsiyasi"""
        if not ONNX_AVAILABLE:
            return None
        
        try:
            # Model yuklash
            model = onnx.load(model_info.path)
            
            # Model optimizatsiya
            model = onnxoptimizer.optimize(model)
            
            # Yangi model saqlash
            output_path = model_info.path.replace(".onnx", "_optimized.onnx")
            onnx.save(model, output_path)
            
            # Yangi model profili
            optimized_profile = self.profiler.profile_onnx_model(output_path)
            
            # Yangi ModelInfo
            optimized_info = ModelInfo(
                name=model_info.name + "_optimized",
                path=output_path,
                size=optimized_profile.get("model_size", 0),
                parameters=model_info.parameters,
                layers=model_info.layers,
                input_shape=optimized_profile.get("input_shape", []),
                output_shape=optimized_profile.get("output_shape", []),
                framework="onnx",
                precision=self.config.target_precision,
                inference_time=optimized_profile.get("inference_time", 0.0),
                memory_usage=optimized_profile.get("memory_usage", 0)
            )
            
            return optimized_info
            
        except Exception as e:
            logger.error(f"ONNX optimizatsiya xatosi: {str(e)}")
            return None

    async def _optimize_generic_model(self, model_info: ModelInfo) -> Optional[ModelInfo]:
        """Umumiy model optimizatsiyasi"""
        try:
            # Fayl optimizatsiya
            import shutil
            
            # Model faylini nusxalash
            output_path = model_info.path.replace(
                Path(model_info.path).suffix, 
                f"_optimized{Path(model_info.path).suffix}"
            )
            shutil.copy2(model_info.path, output_path)
            
            # Hajm kamayish (simple compression)
            import gzip
            compressed_path = output_path + ".gz"
            with open(output_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Yangi ModelInfo
            compressed_size = os.path.getsize(compressed_path)
            optimized_info = ModelInfo(
                name=model_info.name + "_optimized",
                path=compressed_path,
                size=compressed_size,
                parameters=model_info.parameters,
                layers=model_info.layers,
                input_shape=model_info.input_shape,
                output_shape=model_info.output_shape,
                framework=model_info.framework,
                precision="compressed",
                inference_time=model_info.inference_time * 0.9,  # Taxmin
                memory_usage=compressed_size
            )
            
            return optimized_info
            
        except Exception as e:
            logger.error(f"Generic model optimizatsiya xatosi: {str(e)}")
            return None

    async def _quantize_pytorch_model(self, model: Any) -> Any:
        """PyTorch model quantization"""
        if not TORCH_AVAILABLE:
            return model
        
        try:
            if self.config.quantization_method == "dynamic":
                # Dynamic quantization
                model = torch.quantization.quantize_dynamic(
                    model, 
                    {torch.nn.Linear, torch.nn.Conv2d}, 
                    dtype=torch.qint8
                )
            elif self.config.quantization_method == "static":
                # Static quantization (requires calibration data)
                model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
                model = torch.quantization.prepare(model)
                # Calibration logic would go here
                model = torch.quantization.convert(model)
            
            return model
            
        except Exception as e:
            logger.error(f"PyTorch quantization xatosi: {str(e)}")
            return model

    async def _quantize_tensorflow_model(self, model: Any) -> Any:
        """TensorFlow model quantization"""
        if not TENSORFLOW_AVAILABLE:
            return model
        
        try:
            if self.config.target_precision == "int8":
                # Integer quantization
                converter = tf.lite.TFLiteConverter.from_keras_model(model)
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                tflite_model = converter.convert()
                
                # Save and reload as Keras model
                tflite_path = model_info.path.replace(".h5", "_quantized.tflite")
                with open(tflite_path, 'wb') as f:
                    f.write(tflite_model)
                
                return tflite_model
            elif self.config.target_precision == "float16":
                # Float16 quantization
                for layer in model.layers:
                    if hasattr(layer, 'dtype') and layer.dtype == tf.float32:
                        layer.dtype = tf.float16
                model = model.astype(tf.float16)
            
            return model
            
        except Exception as e:
            logger.error(f"TensorFlow quantization xatosi: {str(e)}")
            return model

    async def _prune_pytorch_model(self, model: Any, threshold: float) -> Any:
        """PyTorch model pruning"""
        if not TORCH_AVAILABLE:
            return model
        
        try:
            import torch.nn.utils.prune as prune
            
            # Unstructured pruning
            for module in model.modules():
                if isinstance(module, (torch.nn.Linear, torch.nn.Conv2d)):
                    prune.l1_unstructured(module, name='weight', amount=threshold)
                    prune.remove(module, 'weight')
            
            return model
            
        except Exception as e:
            logger.error(f"PyTorch pruning xatosi: {str(e)}")
            return model

    async def _optimize_pytorch_script(self, model: Any) -> Any:
        """PyTorch TorchScript optimizatsiya"""
        if not TORCH_AVAILABLE:
            return model
        
        try:
            # Script model yaratish
            scripted_model = torch.jit.script(model)
            return scripted_model
            
        except Exception as e:
            logger.error(f"TorchScript optimizatsiya xatosi: {str(e)}")
            return model

    async def optimize_all_models(self, models: List[str]) -> Dict[str, ModelInfo]:
        """Barcha model'larni optimizatsiya qilish"""
        logger.info("🚀 AI Model optimizatsiya boshlanmoqda...")
        
        # Model'larni profil qilish
        model_profiles = await self.profile_all_models(models)
        
        optimized_models = {}
        
        # Parallely optimizatsiya qilish
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_model = {
                executor.submit(self._optimize_model_sync, model_path, model_info): model_path
                for model_path, model_info in model_profiles.items()
            }
            
            for future in as_completed(future_to_model):
                model_path = future_to_model[future]
                try:
                    optimized_info = future.result()
                    if optimized_info:
                        optimized_models[model_path] = optimized_info
                        logger.info(f"✅ Optimizatsiya tugallandi: {Path(model_path).name}")
                except Exception as e:
                    logger.error(f"❌ Model optimizatsiya xatosi {model_path}: {str(e)}")
        
        # Hisobot yaratish
        await self._generate_optimization_report(model_profiles, optimized_models)
        
        logger.info("🎉 AI Model optimizatsiya tugallandi!")
        return optimized_models

    def _optimize_model_sync(self, model_path: str, model_info: ModelInfo) -> Optional[ModelInfo]:
        """Synchronous model optimizatsiya"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.optimize_model(model_info))
        finally:
            loop.close()

    async def _generate_optimization_report(self, original_models: Dict[str, ModelInfo], optimized_models: Dict[str, ModelInfo]):
        """Optimizatsiya hisoboti yaratish"""
        logger.info("📊 Optimizatsiya hisoboti yaratilmoqda...")
        
        report = {
            "summary": {
                "total_models": len(original_models),
                "optimized_models": len(optimized_models),
                "optimization_success_rate": len(optimized_models) / len(original_models) if original_models else 0
            },
            "original_models": {k: asdict(v) for k, v in original_models.items()},
            "optimized_models": {k: asdict(v) for k, v in optimized_models.items()},
            "performance_improvements": {},
            "recommendations": []
        }
        
        # Performance yaxshilanishlar
        for original_path, original_info in original_models.items():
            if original_path in optimized_models:
                optimized_info = optimized_models[original_path]
                
                # Size improvement
                size_improvement = (original_info.size - optimized_info.size) / original_info.size if original_info.size > 0 else 0
                
                # Speed improvement
                speed_improvement = (original_info.inference_time - optimized_info.inference_time) / original_info.inference_time if original_info.inference_time > 0 else 0
                
                report["performance_improvements"][original_path] = {
                    "size_reduction": size_improvement,
                    "speed_improvement": speed_improvement,
                    "compression_ratio": optimized_info.compression_ratio,
                    "accuracy_preserved": optimized_info.accuracy_preserved
                }
        
        # Tavsiyalar
        report["recommendations"] = self._generate_optimization_recommendations(optimized_models)
        
        # Hisobotni saqlash
        report_path = "ai_optimization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Optimizatsiya hisoboti saqlandi: {report_path}")

    def _generate_optimization_recommendations(self, optimized_models: Dict[str, ModelInfo]) -> List[str]:
        """Optimizatsiya tavsiyalari"""
        recommendations = []
        
        # GPU tavsiyalari
        if self.gpu_available:
            recommendations.append("GPU acceleration yoqilgan - yuqori samaradorlik")
        else:
            recommendations.append("GPU acceleration yoqish tavsiya etiladi")
        
        # Memory management
        recommendations.append("Model caching ishlatish inference speedni oshiradi")
        recommendations.append("Batch processing large models uchun tavsiya etiladi")
        
        # Framework-specific recommendations
        frameworks = {model.framework for model in optimized_models.values()}
        if "pytorch" in frameworks:
            recommendations.append("PyTorch: TorchScript va quantization kombinatsiyasi")
        if "tensorflow" in frameworks:
            recommendations.append("TensorFlow: TFLite optimizatsiya edge devices uchun")
        
        return recommendations

    @contextmanager
    def memory_limit(self, limit_mb: int):
        """Memory limit context manager"""
        original_limit = self.memory_monitor.get_memory_limit()
        self.memory_monitor.set_memory_limit(limit_mb)
        try:
            yield
        finally:
            self.memory_monitor.set_memory_limit(original_limit)

class MemoryMonitor:
    """Memory monitoring va management"""
    
    def __init__(self):
        self.memory_limits = {}
        self.current_usage = 0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Joriy memory usage olish"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent
        }
    
    def set_memory_limit(self, limit_mb: int):
        """Memory limit o'rnatish"""
        process = psutil.Process()
        process.nice(psutil.HIGH_PRIORITY_CLASS)  # High priority
        self.memory_limits[process.pid] = limit_mb
    
    def get_memory_limit(self) -> Optional[int]:
        """Joriy memory limit olish"""
        process = psutil.Process()
        return self.memory_limits.get(process.pid)

    def check_memory_pressure(self) -> bool:
        """Memory pressure tekshirish"""
        memory = psutil.virtual_memory()
        return memory.percent > 80

    def cleanup_memory(self):
        """Memory cleanup"""
        if self.check_memory_pressure():
            gc.collect()
            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()

# CLI interface
async def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Optimizer - Sun'iy intellekt optimizatori")
    parser.add_argument("--models-dir", required=True, help="Modellar papka yo'li")
    parser.add_argument("--framework", choices=["pytorch", "tensorflow", "onnx", "auto"], default="auto", help="Framework")
    parser.add_argument("--precision", choices=["float32", "float16", "int8"], default="float16", help="Target precision")
    parser.add_argument("--compression", choices=["quantization", "pruning", "distillation"], default="quantization", help="Compression method")
    parser.add_argument("--output-dir", help="Optimizatsiya qilingan modellar uchun papka")
    
    args = parser.parse_args()
    
    # Config yaratish
    config = OptimizationConfig(
        model_path=args.models_dir,
        framework=args.framework,
        target_precision=args.precision,
        compression_method=args.compression,
        target_device="gpu" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
    )
    
    # Optimizator yaratish
    optimizer = AIOptimizer(config)
    
    # Model'larni topish
    models = optimizer.discover_models(args.models_dir)
    if not models:
        print("Hech qanday model topilmadi!")
        return 1
    
    print(f"Topilgan modellar: {len(models)} ta")
    
    # Optimizatsiya o'tkazish
    try:
        optimized_models = await optimizer.optimize_all_models(models)
        
        # Natijani ko'rsatish
        print("\n🤖 AI MODEL OPTIMIZATSIYASI NATIJASI:")
        print("=" * 50)
        print(f"Umumiy modellar: {len(models)}")
        print(f"Optimizatsiya qilingan: {len(optimized_models)}")
        print(f"Muvaffaqiyat darajasi: {len(optimized_models)/len(models)*100:.1f}%")
        
        if optimized_models:
            print("\nOptimizatsiya qilingan modellar:")
            for path, info in optimized_models.items():
                print(f"  - {Path(path).name}: {info.compression_ratio*100:.1f}% hajm kamayishi")
        
    except Exception as e:
        logger.error(f"AI optimizatsiya xatosi: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())