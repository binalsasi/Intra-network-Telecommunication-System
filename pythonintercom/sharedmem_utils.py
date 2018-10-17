key_tone 	= 60001;
key_offhook 	= 60002;
key_endip 	= 60003;
key_convo 	= 60004;
key_dtmf 	= 60005;
key_inccall 	= 60006;
key_calls 	= 60007;
key_ringphone 	= 60008;
key_phone = 60009;


def write_to_memory(memory, s):
    s += '\0'
    memory.write(s)


def read_from_memory(memory):
    s = memory.read()
    i = s.find('\0')
    if i != -1:
        s = s[:i]

    return s
