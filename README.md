# seastar-gdb

#### Build GDB
It is easiest to do an in-source build in the top-level diectory. After that it
is possible to rebbuild individual components (GDB).

#### Start GDB

As normal, but in addition you need to instruct GDb to use the data directory
which is produced by the same build (`binutils/gdb/data-directory` in case of an
in-source build). You can copy it to another location, as long as you tell GDB
to use it:

    $ gdb --core=./mycore -D /path/to/data-directory /path/to/myexec

#### Use

First, source `seastar-gdb.py`:

    (gdb) source /path/to/seastar-gdb.py

To switch to a thread:

    (gdb) seastar thread $my_seastar_thread_ctx
