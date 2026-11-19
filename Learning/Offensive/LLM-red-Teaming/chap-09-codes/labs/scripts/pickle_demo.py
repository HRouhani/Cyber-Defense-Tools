#!/usr/bin/env python3
"""Harmless pickle loading side effect + static inspection; lab-owned file only."""
import builtins
import pickle
import pickletools
from pathlib import Path

DEST=Path(__file__).resolve().parents[1]/'workspace'/'model_artifacts'

class DemoObject:
    def __reduce__(self):
        # This harmless print happens during unpickling before any inference.
        return (builtins.print, ('[DEMO] An object-loading side effect ran!',))

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    p=DEST/'toy-model.pkl'
    p.write_bytes(pickle.dumps({'tensor_shape': [2,2], 'metadata':DemoObject()}))
    print('Created local synthetic artifact:',p)
    print('\nStatic pickle opcodes mentioning imports/calls:')
    for opcode,arg,_ in pickletools.genops(p.read_bytes()):
        if opcode.name in ('STACK_GLOBAL','GLOBAL','REDUCE'):
            print(' ',opcode.name,repr(arg))
    print('\nIntentionally loading only the locally generated harmless demo:')
    obj=pickle.loads(p.read_bytes())
    print('Loaded keys:',list(obj.keys()))
    print('DO NOT unpickle unknown model files. Use safe formats and scanner/quarantine.')

if __name__=='__main__': main()
