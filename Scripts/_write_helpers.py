import pathlib,base64,sys
path=sys.argv[1]; data=base64.b64decode(sys.argv[2]); pathlib.Path(path).write_bytes(data); print(path, len(data))
