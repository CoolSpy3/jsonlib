# jsonlib
A simple library which builds upon Python's json library.

## Registering Files
To be used, a file must first be registered. This allows it to be opened with an alias without having to use the full path.
```
jsonlib.registerFile(<alias>, <path>)
```

## Reading JSON
To read json, the library provides the context handler `open_json`. This also provides thread synchronization on the requested file.
```
with jsonlib.open_json(<alias>) as json_data:
    pass
```

## Writing JSON
Writing JSON must me done inside the context handler using the `save` method. Keep in mind that the dictionary passed to the `save` method must be the same dictionary as was returned by the context handler. It may be updated either directly or via the dictionary's `update` method.
```
with jsonlib.open_json(<alias>) as json_data:
    # Modify json_data
    jsonlib.save(json_data)
```
