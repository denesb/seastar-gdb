import gdb


def rol(value, shift):
    bits = 64
    value = (value >> (bits - shift)) | (value << shift) & (2**bits - 1)
    return value


def ror(value, shift):
    bits = 64
    value = (value << (bits - shift)) & (2**bits - 1) | (value >> shift)
    return value


def do_mangle(canary, v):
    s1 = v ^ canary
    s2 = rol(s1, 0x11)
    return s2


def do_demangle(canary, v):
    s1 = ror(v, 0x11)
    s2 = s1 ^ canary
    return s2


canary = int(gdb.parse_and_eval('(unsigned long)__pointer_chk_guard_local'))


def mangle(v):
    gdb.write('0x{:016x} -> 0x{:016x}\n'.format(v, int(do_mangle(canary, v))))


def demangle(v):
    gdb.write('0x{:016x} -> 0x{:016x}\n'.format(v, int(do_demangle(canary, v))))


def switch(thread):
    ulong_type = gdb.lookup_type('unsigned long')
    thread = gdb.parse_and_eval(thread)
    thread_ctx = thread['_context']['_M_t']['_M_t']['_M_head_impl'].dereference()
    jmpbuf = thread_ctx['_context']['jmpbuf']['__jmpbuf']

    reg_vals = []
    mangled_regs = [1, 6, 7]
    for reg in range(8):
        if reg in mangled_regs:
            val = do_demangle(canary, jmpbuf[reg].cast(ulong_type))
        else:
            val = jmpbuf[reg].cast(ulong_type)
        reg_vals.append(val)

    gdb.write('switch to (seastar::thread_context*) 0x{:016x}\n'.format(int(thread_ctx.address)))
    cmd = 'fiber select {}'.format(' '.join(['0x{:016x}'.format(int(val)) for val in reg_vals]))
    gdb.write('{}\n'.format(cmd))
    gdb.execute(cmd)


class seastar_thread(gdb.Command):
    """Switch to a seastar thread

    Usage:
    seastar thread $thread

    Where $thread is a convenience variable or expression evaluating to a
    `seastar::thread_context`.
    """

    def __init__(self):
        gdb.Command.__init__(self, 'seastar thread', gdb.COMMAND_USER, gdb.COMPLETE_NONE, True)

    def invoke(self, arg, for_tty):
        switch(arg)
