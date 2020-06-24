This directory contains a set of example systems

# Setup

You will need a folder or subvolume on a BTRFS volume somewhere to proceed.

This is your base folder.

## Work directory setup

Create a new folder 'work' in your base folder.

That will be your work directory going forward.

Clrm *should* not write outside of the work directory, but please run
the whole thing in a VM or a container to make sure it really does not
break anything on your system!

## Borg repository setup

Create a new borg repository in your base folder. The name must be
'borg_repository' for the examples to work.

```
borg init borg_repository --encryption=authenticated
```

Give 'foobar' as a passphrase (or whatever else you want)

Then export that passphrase to the environment.

```
export BORG_PASSPHRASE=foobar
```

## Configuration

Check `type-base/pacstrap.conf` and adjust download servers used,
etc. to your liking.

## Notes

Clrm *should* not write outside of the work directory, but please run
the whole thing in a VM or a container to make sure it really does not
break anything on your system!


# Creating an example image

Run the following command as root:

```
export CLRM_BASE=/absolute/path/to/your/clrm-checkout
export BASE_DIR=/absolute/path/to/your/base-folder

"${CLRM_BASE}/clrm \
    --systems-directory="${CLRM_BASE}/examples" \
    --work-directory="${BASE_DIR}/work" \
    --clear-storage \
    --clear-scratch-directory \
    --repository-base-directory="${BASE_DIR}" \
    system-example
```

This command will take a while: It will do a cleanroom installation
of arch linux according to the system-example definition file.

Feel free to throw in up to four '--verbose' if you want to see lots of
text scroll by.

Leave out '--clear-storage' to keep successfully created systems between
clrm runs. This can greatly speed up debugging of system definitions.

Once this command is complete, you should have a system image in the
borg repository you have set up earlier.

Test with:
```
borg list borg_repository
```

There should be one entry starting with 'system-example-' and a recent timestamp.

# Test the image

Extract the image from borg and start it in qemu.

Either fix permissions on the borg repository to allow access for your normal user
or make sure that root can start UI applications for this to work:

```
export BORG_PASSPHRASE=foobar
"${CLRM_BASE}/firestarter" \
    --repository="${BASE_DIR}/borg_repository \
    system-example qemu-image
```

Log in as root user using password root1234

# Where to go from here

Write your own system definition files based on those found here:-)

"${CLRM_BASE}/clrm --list-commands

should list all the pre-defined commands at your disposal.

Firestarter has several export options for the images stored in borg.
