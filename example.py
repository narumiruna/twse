from twse import get_stock_info


def main() -> None:
    result = get_stock_info("2330")
    print(result)

if __name__ == '__main__':
    main()
