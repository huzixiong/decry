import subprocess


def hexToByte(inHex):
    hexlen = len(inHex)
    result = []
    if (hexlen % 2 == 1):
        hexlen += 1
        inHex = "0" + inHex
    for i in range(0, hexlen, 2):
        result.append(int(inHex[i:i + 2], 16))
    return result


def initKey(aKey):
    state = list(range(256))
    bkey = [ord(i) for i in list(aKey)]
    index1 = 0
    index2 = 0
    if (len(bkey) == 0):
        return []
    for i in range(256):
        index2 = ((bkey[index1] & 0xff) + (state[i] & 0xff) + index2) & 0xff
        state[i], state[index2] = state[index2], state[i]
        index1 = (index1 + 1) % len(bkey)
    return state


def RC4Base(input, mKkey):
    x = 0
    y = 0
    key = initKey(mKkey)
    result = list(range(len(input)))
    for i in range(len(input)):
        x = (x + 1) & 0xff
        y = ((key[x] & 0xff) + y) & 0xff
        key[x], key[y] = key[y], key[x]
        xorIndex = ((key[x] & 0xff) + (key[y] & 0xff)) & 0xff
        result[i] = (input[i] ^ key[xorIndex])
    return result
    
def encryRC4Byte(data, key, chartSet='utf-8'):
    if not chartSet:
        bData = [ord(i) for i in data]
        return RC4Base(bData, key)
    else:
        bData = list(data.encode(chartSet))
        return RC4Base(bData, key)


def decryRC4(data, key='**************', chartSet='utf-8'):
    r = RC4Base(hexToByte(data), key)
    # print(bytes(r).decode(chartSet))
    return bytes(r).decode(chartSet)


def subprocess_exc():
    return subprocess.Popen("adb shell logcat", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)


def decry_uaflogs(file):
    while True:
        sub_file = file.stdout.readline().decode(encoding='utf-8',errors='ignore')
        if sub_file == '':
            print("stdout.readline return None,break")
            return False

        elif sub_file.find('JLog') != -1:
            split_time,split_file = sub_file.rsplit(":", maxsplit=1)
            code_file = split_file.strip()
            decry_log = decryRC4(code_file)
            total_log = ':'.join([split_time,decry_log])
            if total_log.find("Key Step") != -1 or total_log.find("SOFT_SIM") != -1:
                print(total_log)

if __name__ == "__main__":
    f = subprocess_exc()
    decry_uaflogs(f)
