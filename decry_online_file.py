import re
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


def decryRC4(data, key='ukelinkucservice', chartSet='utf-8'):
    r = RC4Base(hexToByte(data), key)
    # print(bytes(r).decode(chartSet))
    return bytes(r).decode(chartSet,errors='ignore')


def encryRC4Byte(data, key, chartSet='utf-8'):
    if not chartSet:
        bData = [ord(i) for i in data]
        return RC4Base(bData, key)
    else:
        bData = list(data.encode(chartSet))
        return RC4Base(bData, key)


def subprocess_exc():
    return subprocess.Popen("adb shell logcat", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)


def re_find_out(args, s):
    pattern = re.compile(args, re.I | re.M)
    str_find_out = re.search(pattern, s)
    if str_find_out == None:
        return False
    else:
        return True


def decry_uaflogs(file, cmd=''):
    while True:
        sub_file = file.stdout.readline().decode(encoding='utf-8', errors='ignore')
        if sub_file == '':
            print("wait for device....")
            return False

        elif sub_file.find('JLog') != -1:
            split_time, split_file = sub_file.rsplit(":", maxsplit=1)
            code_file = split_file.strip()
            decry_log = decryRC4(code_file)
            total_log = ': '.join([split_time, decry_log])
            # print(total_log)
            # if total_log.find("Key Step") != -1 or total_log.find("SOFT_SIM") != -1:
            #     print(total_log)
            if cmd == '':
                print(total_log)
            if re_find_out(cmd,total_log):
                print(total_log)


def main():
    print("""说明：
1、用于uservice log在线抓取，实时解密打印云卡log。请确保设备和电脑通过usb线连接。
2、多个关键字用|隔开,不过滤直接回车。
3、过滤关键字不区分大小写。
4、支持开启多个窗口，每个窗口过滤不同log信息。
-------------------------------------------------
""")

    input_cmd = input("请输入关键字：")

    while True:
        subprocess.getoutput("adb wait-for-device")
        print("device connected")
        logs = subprocess_exc()
        decry_uaflogs(logs,input_cmd)


if __name__ == "__main__":
    main()
