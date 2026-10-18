"""Configuration for the replaceable sentiment model."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.environ.get('REVIEW_MODEL_PATH', PROJECT_ROOT / 'models' / 'sentiment_model.keras')).expanduser()
_DEFAULT_TOKENIZER = PROJECT_ROOT / 'models' / 'bert-base-chinese-model'
_TRAINING_TOKENIZER = Path(r'D:\python_project\bert-base-chinese-model')
TOKENIZER_PATH = Path(os.environ.get(
    'REVIEW_TOKENIZER_PATH',
    _DEFAULT_TOKENIZER if _DEFAULT_TOKENIZER.is_dir() else _TRAINING_TOKENIZER
)).expanduser()
LABELS = ('差评', '中评', '好评')
RATING_TO_LABEL = {1: 0, 2: 0, 3: 1, 4: 2, 5: 2}
MAX_CONFIDENCE_FOR_REVIEW = float(os.environ.get('REVIEW_CONFIDENCE_THRESHOLD', '0.65'))
MAX_SEQUENCE_LENGTH = int(os.environ.get('REVIEW_MAX_SEQUENCE_LENGTH', '100'))
