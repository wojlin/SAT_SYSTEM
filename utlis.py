def read_file(_path):
    try:
        with open(_path, 'r') as _file:
            return _file.read()
    except Exception as e:
        raise Exception(e)