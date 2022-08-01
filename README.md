## Canvas API Wrapper

This is a CLI wrapper around the [Canvas LMS API](https://canvas.instructure.com/doc/api/index.html)

## Installation
Installation requires Python 3.10

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
default="<nickname>"

[instance.<nickname>]
domain="domain.instructure.com"
token="<API TOKEN>"
```

To test that it's configured properly you can execute

```
$ canvas get users/self
```

And confirm that the output is for your user

### Canvas Instances
Each customer or entity that Instructure deals with is given their own Canvas instance with a unique domain name. Each instance is added to your configuration like so:
```toml
[instance.<nickname>]
domain="domain.instructure.com"
token="<API TOKEN>"
```

The Canvas instance to use can then be selected when running a query
```
$ canvas get users/self -i <nickname>
```

If no instance is specified then the default will be used. If the configuration does not have a default, then you must specific an instance with every query
```toml
[instance]
default="<nickname>"

[instance.<nickname>]
domain="domain.instructure.com"
token="<API TOKEN>"
```

## Usage
You can query Canvas endpoints using the `query` subcommand and it's aliases (`get`, `post`, `put` and `delete`)

```
$ canvas get <endpoint>
```

The `endpoint` parameter will simply be the unique part of the API url.
For example: The URL: `https://canvas.instructure.com/api/v1/accounts/:account_id/users` would be queried as
```
$ canvas get accounts/:account_id/users
```
### Query Parameters
Query Parameters are added using the `-q` option

```
$ canvas get :course_id/assignments -q include[]=submission -q all_dates=true
```

### Request Body
The request body for POST or PUT requests is passed in via the `-d` option

Either as a JSON string:
```
$ canvas put courses/:course_id/assignments/:assignment_id  -d '
     {
       "assignment": {
         "name": "New Test Name"
       }
     }
     '
```

Or a filename
```
$ canvas put courses/:course_id/assignments/:assignment_id  -d @file.json
```


### Piping
When you pipe the output of `canvas` to another program, syntax highlighting will not be added. This is convenient, because it allows you to pipe to other programs like `jq` very easily.
Additionally, any info that is not the JSON response from Canvas is written to `stderr` instead of `stdout`, so you don't have to worry abou those

The JSON output will still be formatted. If you want to disable all of that you can use the `--raw` flag