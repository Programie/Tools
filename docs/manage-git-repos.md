# manage-git-repos

manage-git-repos allows you to store and restore a list of git repositories. This is useful if you are using multiple computers where you want to keep those repositories in sync.

The script has two commands: `store` and `restore`

## Store current list of git repositories

The command `store` creates a list of your current git repositories and saves it into a file.

## Restore list of git repositories

The command `restore` reads the previously created file and clones any git repository listed in that file.

By adding `--pull`, the script also makes sure that each repository is up-to-date (i.e. pulls each of them which is already existing).

Adding the option `--purge` removes repositories not listed in that file.

You may also use `--dryrun` to see what would be done without actually doing that (can also be combined with the other options, i.e. to see which repositories will be pulled or purged).