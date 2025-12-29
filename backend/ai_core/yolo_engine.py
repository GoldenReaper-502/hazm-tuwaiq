"""
HAZM TUWAIQ - YOLOv8 Detection Engine
Real Computer Vision with Ultralytics YOLOv8
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("⚠️ Ultralytics not available. Install: pip install ultralytics")


class YOLOEngine:
    """
    محرك كشف الأجسام باستخدام YOLOv8
    Real YOLOv8 detection for safety monitoring
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.25):
        """
        Initialize YOLOv8 engine
        
        Args:
            model_path: Path to YOLOv8 model weights
            confidence_threshold: Minimum confidence for detections
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        # PPE class mappings (custom trained model would have these)
        self.ppe_classes = {
            'person': 0,
            'hardhat': 1,
            'safety_vest': 2,
            'safety_glasses': 3,
            'gloves': 4,
            'safety_boots': 5,
            'mask': 6,
            'no_hardhat': 7,
            'no_safety_vest': 8
        }
        
        # Vehicle classes
        self.vehicle_classes = {
            'car': 2,
            'truck': 7,
            'forklift': 80,  # Custom class
            'excavator': 81  # Custom class
        }
        
        # Initialize model
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load YOLOv8 model"""
        try:
            if not YOLO_AVAILABLE:
                self.logger.warning("YOLOv8 not available - using simulation mode")
                return False
            
            # Try to load model
            model_file = Path(self.model_path)
            
            if not model_file.exists():
                self.logger.info(f"Model not found at {self.model_path}, downloading YOLOv8n...")
                # YOLO will auto-download if not exists
                self.model = YOLO('yolov8n.pt')
            else:
                self.logger.info(f"Loading model from {self.model_path}")
                self.model = YOLO(self.model_path)
            
            self.logger.info("✅ YOLOv8 model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load YOLOv8: {e}")
            return False
    
    def detect(self, image: np.ndarray, detect_ppe: bool = True) -> Dict[str, Any]:
        """
        Detect objects in image
        
        Args:
            image: Input image (BGR format)
            detect_ppe: Whether to detect PPE violations
            
        Returns:
            Detection results with bounding boxes, classes, and confidence
        """
        if self.model is None:
            return self._simulate_detection(image)
        
        try:
            # Run YOLOv8 detection
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            
            # Parse results
            detections = self._parse_results(results[0], detect_ppe)
            
            # Analyze PPE compliance if requested
            if detect_ppe:
                ppe_analysis = self._analyze_ppe_compliance(detections)
                detections['ppe_compliance'] = ppe_analysis
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            return self._simulate_detection(image)
    
    def _parse_results(self, result, detect_ppe: bool = True) -> Dict[str, Any]:
        """Parse YOLO detection results"""
        
        detections = {
            'objects': [],
            'people_count': 0,
            'vehicle_count': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if result.boxes is None or len(result.boxes) == 0:
            return detections
        
        # Extract detections
        boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
        confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
        class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs
        
        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            # Get class name
            class_name = result.names[cls_id]
            
            # Create detection object
            detection = {
                'class': class_name,
                'confidence': float(conf),
                'bbox': {
                    'x1': float(box[0]),
                    'y1': float(box[1]),
                    'x2': float(box[2]),
                    'y2': float(box[3])
                }
            }
            
            detections['objects'].append(detection)
            
            # Count specific categories
            if class_name == 'person':
                detections['people_count'] += 1
            elif class_name in ['car', 'truck', 'bus']:
                detections['vehicle_count'] += 1
        
        return detections
    
    def _analyze_ppe_compliance(self, detections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze PPE compliance for detected people
        
        Args:
            detections: Detection results
            
        Returns:
            PPE compliance analysis
        """
        people_count = detections['people_count']
        
        if people_count == 0:
            return {
                'compliant': True,
                'compliance_rate': 1.0,
                'violations': [],
                'total_people': 0
            }
        
        # Count PPE items
        hardhat_count = 0
        vest_count = 0
        violations = []
        
        for obj in detections['objects']:
            if obj['class'] in ['hardhat', 'helmet']:
                hardhat_count += 1
            elif obj['class'] in ['safety_vest', 'vest']:
                vest_count += 1
            elif obj['class'] == 'no_hardhat':
                violations.append({
                    'type': 'NO_HELMET',
                    'confidence': obj['confidence'],
                    'location': obj['bbox']
                })
            elif obj['class'] == 'no_safety_vest':
                violations.append({
                    'type': 'NO_SAFETY_VEST',
                    'confidence': obj['confidence'],
                    'location': obj['bbox']
                })
        
        # Calculate compliance
        # Assuming each person should have helmet and vest
        expected_ppe = people_count * 2  # helmet + vest per person
        detected_ppe = hardhat_count + vest_count
        
        compliance_rate = min(detected_ppe / expected_ppe, 1.0) if expected_ppe > 0 else 0.0
        
        return {
            'compliant': compliance_rate >= 0.8,  # 80% threshold
            'compliance_rate': round(compliance_rate, 2),
            'violations': violations,
            'total_people': people_count,
            'helmets_detected': hardhat_count,
            'vests_detected': vest_count
        }
    
    def _simulate_detection(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Simulation mode when YOLOv8 is not available
        Returns realistic simulated data
        """
        height, width = image.shape[:2]
        
        # Simulate 2-5 people
        people_count = np.random.randint(2, 6)
        vehicle_count = np.random.randint(0, 3)
        
        objects = []
        
        # Add people
        for i in range(people_count):
            x1 = np.random.randint(0, width - 100)
            y1 = np.random.randint(0, height - 200)
            objects.append({
                'class': 'person',
                'confidence': np.random.uniform(0.85, 0.98),
                'bbox': {
                    'x1': float(x1),
                    'y1': float(y1),
                    'x2': float(x1 + 80),
                    'y2': float(y1 + 180)
                }
            })
        
        # Add vehicles
        for i in range(vehicle_count):
            x1 = np.random.randint(0, width - 200)
            y1 = np.random.randint(0, height - 150)
            objects.append({
                'class': np.random.choice(['car', 'truck', 'forklift']),
                'confidence': np.random.uniform(0.80, 0.95),
                'bbox': {
                    'x1': float(x1),
                    'y1': float(y1),
                    'x2': float(x1 + 180),
                    'y2': float(y1 + 120)
                }
            })
        
        # Simulate PPE detection
        helmet_count = int(people_count * 0.7)  # 70% have helmets
        vest_count = int(people_count * 0.8)    # 80% have vests
        
        violations = []
        if helmet_count < people_count:
            violations.append({
                'type': 'NO_HELMET',
                'confidence': 0.89,
                'location': objects[0]['bbox'] if objects else {}
            })
        
        return {
            'objects': objects,
            'people_count': people_count,
            'vehicle_count': vehicle_count,
            'timestamp': datetime.now().isoformat(),
            'ppe_compliance': {
                'compliant': len(violations) == 0,
                'compliance_rate': 0.75,
                'violations': violations,
                'total_people': people_count,
                'helmets_detected': helmet_count,
                'vests_detected': vest_count
            },
            'simulation_mode': True
        }
    
    def detect_from_file(self, image_path: str) -> Dict[str, Any]:
        """
        Detect objects from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Detection results
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            return self.detect(image)
            
        except Exception as e:
            self.logger.error(f"Error detecting from file: {e}")
            return {'error': str(e)}
    
    def detect_video_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detect objects in video frame
        Optimized for real-time processing
        
        Args:
            frame: Video frame (BGR)
            
        Returns:
            Detection results
        """
        return self.detect(frame, detect_ppe=True)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model"""
        return {
            'model_loaded': self.model is not None,
            'model_path': self.model_path,
            'confidence_threshold': self.confidence_threshold,
            'yolo_available': YOLO_AVAILABLE,
            'supported_classes': len(self.model.names) if self.model else 0
        }


# Singleton instance
_yolo_engine: Optional[YOLOEngine] = None


def get_yolo_engine(model_path: str = "yolov8n.pt") -> YOLOEngine:
    """
    Get singleton YOLOEngine instance
    
    Args:
        model_path: Path to model weights
        
    Returns:
        YOLOEngine instance
    """
    global _yolo_engine
    
    if _yolo_engine is None:
        _yolo_engine = YOLOEngine(model_path=model_path)
    
    return _yolo_engine
