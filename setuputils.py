import codecs
import os.path


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(file_path, 'r') as fobj:
        content = fobj.read()
    return content
