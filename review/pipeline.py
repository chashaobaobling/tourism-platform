"""Model-independent decision rules used by CSV and crawler review flows."""
from . import config
from . import model_adapter


def predict_and_compare(rows):
    """Annotate rows; never changes or overwrites the source rating."""
    predictions = model_adapter.predict([row.get('comment', '') for row in rows])
    results = []
    for row, prediction in zip(rows, predictions):
        item = dict(row)
        score = int(item['sentiment_score'])
        source_class = config.RATING_TO_LABEL.get(score)
        agrees = source_class == prediction['class_index']
        identity_status = item.get('identity_status', 'new')
        item.update({
            'source_rating': score,
            'source_class': config.LABELS[source_class] if source_class is not None else None,
            'model_predicted_class': prediction['predicted_class'],
            'model_confidence': prediction['confidence'],
            'model_probabilities': prediction['probabilities'],
            'rating_agrees': agrees,
            'review_status': 'auto_pass' if (
                agrees and prediction['confidence'] >= config.MAX_CONFIDENCE_FOR_REVIEW
                and identity_status in {'new', 'matched'}
            ) else 'needs_review',
            'reviewed_rating': None,
            'review_note': None,
        })
        results.append(item)
    return results
