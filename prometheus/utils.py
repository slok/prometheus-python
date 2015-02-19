import collections
from datetime import datetime, timezone


def unify_labels(labels, const_labels, ordered=False):
    if const_labels:
        result = const_labels.copy()
        if labels:
            # Add labels to const labels
            for k, v in labels.items():
                result[k] = v
    else:
        result = labels

    if ordered and result:
        result = collections.OrderedDict(sorted(result.items(),
                                                key=lambda t: t[0]))

    return result


def get_timestamp():
    """ Timestamp is the number of milliseconds since the epoch
        (1970-01-01 00:00 UTC) excluding leap seconds.
    """
    return int(datetime.utcnow().replace(
        tzinfo=timezone.utc).timestamp() * 1000)
