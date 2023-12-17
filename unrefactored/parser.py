import os
from src.handlers.AustrianHandler import AustrianHandler
from src.handlers.NorwegianHandler import NorwegianHandler

if __name__ == '__main__':
    handler = AustrianHandler()
    # # handler.run()
    os.makedirs(handler.OUTPUT_DIR, exist_ok=True)
    for name, payload in handler.render_scs():
        with open(f'{handler.OUTPUT_DIR}{name}.scs', 'w', encoding="utf-8") as file:
            file.write(payload)
