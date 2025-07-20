zipit
============

The challenge gives you the ability to unzip user provided zip files using `7z` and `unzip`. Each of these has its own advantages:

* `unzip` doesn't have security checks for symlinks, and in this case it is run with `-:` option which allows path traversal in zip entries
* `7z` has multidisk archive functionality.

The general exploitation technique is to construct a multidisk archive by unzipping a file with `unzip`, and then extract that multidisk archive using `7z`. We use path traversal to put the multidisk files (`.z01`, `.z02`, etc) in the correct directory.
Once we do that, we use `z02` as a symlink to `/flag`. Then when `7z` tries to extract the multidisk archive, the second disk of the archive will point to `/flag`, so it will think the data it needs to write is the flag.
Then the application will zip the created file and send it back to us, giving us the flag.

The reason this works is that `.z01`, `.z02`, `.zip` are basically slices of a larger zip file. We can put the appropriate zip file headers in `z01` to setup for the file data in `z02`, and the finishing zip metadata in the `.zip` file.

PS. for the multidisk to work all the files need to have the same name. As the name is deterministic on the sha hash of the contents, it is trivial to predict the name that our file will be.

Refer to `exploit.py` for technical implementation details.
