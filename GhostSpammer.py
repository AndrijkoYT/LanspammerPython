import socket, os, re, sys, threading, time, struct, zlib, random
from colorama import Fore, Style, init

init(autoreset=True)

# --- CONFIG ---
LAST_DATA = "None"
VOTE_COUNT = 0
RUNNING_SPAM = False
RUNNING_VOTE = False
SERVERS_LIST = "servers.txt"

# Цвета
C_BRD = Fore.CYAN + Style.BRIGHT
C_VAL = Fore.GREEN + Style.BRIGHT
C_ERR = Fore.RED + Style.BRIGHT
C_TXT = Fore.WHITE + Style.BRIGHT
C_DIM = Fore.BLACK + Style.BRIGHT
C_OFF = Style.RESET_ALL

def cls(): os.system('cls' if os.name == 'nt' else 'clear')

def get_base_name():
    if os.path.exists(SERVERS_LIST):
        try:
            with open(SERVERS_LIST, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip()]
                if lines: return random.choice(lines)
        except: pass
    return "§bVOID-PROJECT"

# --- [VOTE ENGINE: KICK & COUNT] ---
def vote_listener():
    global VOTE_COUNT, LAST_DATA
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(('0.0.0.0', 25565))
        srv.listen(10)
    except: return

    while RUNNING_VOTE:
        try:
            client, addr = srv.accept()
            VOTE_COUNT += 1
            LAST_DATA = f"VOTE FROM {addr[0]}"
            
            # Minecraft Legacy Kick Packet (0xFF)
            reason = f"§a§lГолос учтен! \n§fВсего голосов: §6§l{VOTE_COUNT}"
            payload = b'\xff' + struct.pack('>H', len(reason)) + reason.encode('utf-16be')
            
            client.send(payload)
            client.close()
        except: pass

# --- [SPAM ENGINE: AUTO-TAGS & VOTE] ---
def spam_engine():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    tags = ["[OPEN]", "[NEW]", "[1.21]", "[⚡]", "[FREE]", "[NO-AUTH]"]
    
    while RUNNING_SPAM:
        try:
            base_name = get_base_name()
            
            if RUNNING_VOTE:
                # Режим голосования: фиксированный тег и счетчик
                full_motd = f"§6§l[VOTE] §f{base_name} §7| §e§lГолосов: {VOTE_COUNT}"
            else:
                # Обычный спам: рандомные теги
                tag = random.choice(tags)
                full_motd = f"{tag} §f{base_name} {tag}"

            payload = f'[MOTD]{full_motd}[/MOTD][AD]25565[/AD]'.encode()
            sock.sendto(payload, ('255.255.255.255', 4445))
            time.sleep(0.3)
        except: time.sleep(1)

# --- [MAIN UI] ---
def main():
    global RUNNING_SPAM, RUNNING_VOTE, VOTE_COUNT
    while True:
        cls()
        print(f"{C_BRD}╔" + "═" * 58 + "╗")
        print(f"{C_BRD}║ {C_VAL}VOID-REAPER v21.0 {C_BRD}| {C_TXT}AUTO-SPAM & VOTE SYSTEM         {C_BRD}║")
        print(f"{C_BRD}╠" + "═" * 58 + "╣")
        print(f"{C_BRD}║ {C_TXT}[1] TOGGLE SPAM   {C_DIM}(LAN Broadcast) {C_BRD}: [{C_VAL}{'ON' if RUNNING_SPAM else 'OFF'}{C_BRD}]        ║")
        print(f"{C_BRD}║ {C_TXT}[2] VOTE MODE     {C_DIM}(Kick & Count)  {C_BRD}: [{C_VAL}{'ON' if RUNNING_VOTE else 'OFF'}{C_BRD}]        ║")
        print(f"{C_BRD}║ {C_TXT}[3] RESET VOTE    {C_DIM}(Votes to 0)                           {C_BRD}║")
        print(f"{C_BRD}║ {C_TXT}[4] EXIT                                           {C_BRD}║")
        print(f"{C_BRD}╚" + "═" * 58 + "╝")
        print(f"\n {C_TXT}VOTES: {C_VAL}{VOTE_COUNT} {C_OFF}| {C_TXT}LAST: {Fore.YELLOW}{LAST_DATA}")

        choice = input(f"\n {C_BRD}reaper > {C_OFF}")

        if choice == "1":
            RUNNING_SPAM = not RUNNING_SPAM
            if RUNNING_SPAM: threading.Thread(target=spam_engine, daemon=True).start()
        elif choice == "2":
            RUNNING_VOTE = not RUNNING_VOTE
            if RUNNING_VOTE: threading.Thread(target=vote_listener, daemon=True).start()
        elif choice == "3":
            VOTE_COUNT = 0
        elif choice == "4":
            os._exit(0)

if __name__ == "__main__":
    main()