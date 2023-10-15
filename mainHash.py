from md5Hash import MD5


def main():
    string = str(int(MD5.hash("abc1"), 16))

    num = MD5.hash("dfg")
    print(str(num))


if __name__ == "__main__":
    main()