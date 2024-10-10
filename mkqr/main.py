import qrcode


def main() -> int:
    data = "https://chtbtshwcs.streamlit.app/"
    qr = qrcode.make(data)
    qr.save("qr.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
