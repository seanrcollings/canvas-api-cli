## Canvas API Wrapper

This is a CLI wrapper around the [Canvas LMS API](https://canvas.instructure.com/doc/api/index.html)

## Installation

```
$ pip install canvas-api-cli
```

```
$ canvas --help
```

## Configuration
The config file should be located at `$HOME/.config/canvas.toml`, and look something like this:
```toml
[instance]
default=<nickname>

[instance.<nickname>]
domain=domain.instructure.com
token=<API TOKEN>
```

To test that it's configured properly you can execute

```
$ canvas g users/self
```

And confirm that the output is for your user

### Canvas Instances
Each customer or entity that Instructure deals with is given their own Canvas instance with a unique domain name. Each instance is added to your configuration like so:
```toml
[instance.<nickname>]
domain=domain.instructure.com
token=<API TOKEN>
```

The Canvas instance to use can then be selected when running a query
```
$ canvas g users/self -i <nickname>
```

If no instance is specified then the default will be used. If the configuration does not have a default, then you must specific an instance with every query
```toml
[instance]
default=<nickname>

[instance.<nickname>]
domain=domain.instructure.com
token=<API TOKEN>
```

## Usage