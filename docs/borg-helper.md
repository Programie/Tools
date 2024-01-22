# borg-helper

borg-helper is a script which allows you to define a list of repositories for [borgbackup](https://www.borgbackup.org) and execute borg commands on those repositories.

The script looks for configs at the following locations (merged in that order):

* `/etc/borg-helper.json`
* `~/.config/borg-helper.json`
* `borg-helper.json` in the current directory

The configuration is in JSON and expects at least a `repositories` property containing a map with all of your repositories. Each entry consists of a key (the repository name) and the configuration for this repository.

The repository configuration should have at least a `repository` property specifying the location of that repository. But you might also specify `passphrase` to define the passphrase of that repository as well as `ssh_key` to define the location of your SSH key if using SSH for the repository.

If your borg binary is not in the default search paths, you might specify the path to it using the `borg-binary` property.

## Example configuration

```json
{
  "borg-binary": "/path/to/borg",
  "repositories": {
    "my-repository": {
      "repository": "/path/to/your/repository"
    },
    "another-repository": {
      "repository": "ssh://user@example.com/path/to/repository",
      "passphrase": "YourBorgPassphrase"
    }
  }
}
```

## Usage

To list your configured repositories, execute `borg-helper.py list`.

The example from above will show the following output:
```
Available repositories:
  another-repository (ssh://user@example.com/path/to/repository)
  my-repository (/path/to/your/repository)
```

To execute borg on a specific repository, execute `borg-helper.py <repository> <arguments>`.

Keeping the example from above, `borg-helper.py my-repository info` will execute `borg info` on the repository `my-repository` located at `/path/to/your/repository`. It is basically the same as executing `borg info /path/to/your/repository`.