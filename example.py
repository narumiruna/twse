from twse import get_stock_info_sync


def main() -> None:
    result = get_stock_info_sync("2330")
    print(result.pretty_repr())


if __name__ == "__main__":
    main()
