"""Adapter for the saved two-input Chinese BERT sentiment classifier."""
import threading

import numpy as np

from . import config

_model = None
_tokenizer = None
_model_mtime = None
_lock = threading.Lock()


def _load_runtime():
    global _model, _tokenizer, _model_mtime
    if not config.MODEL_PATH.is_file():
        raise FileNotFoundError(f'模型文件不存在：{config.MODEL_PATH}')
    vocab_path = config.TOKENIZER_PATH / 'vocab.txt'
    if not vocab_path.is_file():
        raise FileNotFoundError(f'分词器词表不存在：{vocab_path}。请设置 REVIEW_TOKENIZER_PATH。')
    mtime = config.MODEL_PATH.stat().st_mtime
    with _lock:
        if _model is None or _model_mtime != mtime:
            try:
                import tensorflow as tf
            except ImportError as exc:
                raise RuntimeError('当前 Python 环境未安装 TensorFlow；请按 requirements-review.txt 安装审核依赖。') from exc
            try:
                from transformers import BertTokenizer, TFBertModel
            except ImportError as exc:
                raise RuntimeError('当前 Python 环境未安装 Transformers；请按 requirements-review.txt 安装审核依赖。') from exc

            _tokenizer = BertTokenizer.from_pretrained(
                str(config.TOKENIZER_PATH), local_files_only=True
            )
            _model = tf.keras.models.load_model(
                config.MODEL_PATH,
                custom_objects={'TFBertModel': TFBertModel},
                compile=False,
            )
            input_names = {tensor.name.split(':')[0].split('/')[-1] for tensor in _model.inputs}
            if input_names != {'input_ids', 'attention_mask'}:
                raise ValueError(f'模型输入应为 input_ids 与 attention_mask，实际为：{sorted(input_names)}')
            if int(_model.output_shape[-1]) != len(config.LABELS):
                raise ValueError(f'模型输出类别数应为 {len(config.LABELS)}，实际为 {_model.output_shape[-1]}')
            _model_mtime = mtime
    return _model, _tokenizer


def model_status():
    try:
        model, _ = _load_runtime()
        return {
            'available': True,
            'path': str(config.MODEL_PATH),
            'tokenizer_path': str(config.TOKENIZER_PATH),
            'output_classes': int(model.output_shape[-1]),
            'labels': list(config.LABELS),
        }
    except Exception as exc:
        return {
            'available': False,
            'path': str(config.MODEL_PATH),
            'tokenizer_path': str(config.TOKENIZER_PATH),
            'message': str(exc),
            'labels': list(config.LABELS),
        }


def predict(texts):
    model, tokenizer = _load_runtime()
    encoded = tokenizer(
        [str(value or '') for value in texts],
        max_length=config.MAX_SEQUENCE_LENGTH,
        padding='max_length',
        truncation=True,
        return_tensors='np',
    )
    model_inputs = {
        'input_ids': np.asarray(encoded['input_ids'], dtype=np.int32),
        'attention_mask': np.asarray(encoded['attention_mask'], dtype=np.int32),
    }
    probabilities = np.asarray(model.predict(model_inputs, verbose=0))
    if probabilities.ndim != 2 or probabilities.shape[1] != len(config.LABELS):
        actual = probabilities.shape[-1] if probabilities.ndim else 'unknown'
        raise ValueError(f'模型输出类别数应为 {len(config.LABELS)}，实际为 {actual}')
    results = []
    for row in probabilities:
        index = int(np.argmax(row))
        results.append({
            'class_index': index,
            'predicted_class': config.LABELS[index],
            'confidence': float(row[index]),
            'probabilities': {label: float(row[i]) for i, label in enumerate(config.LABELS)},
        })
    return results
