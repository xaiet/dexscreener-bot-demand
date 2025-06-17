def format_mcap(m):
    if not m:
        return "?"
    if m > 1_000_000:
        return f"${round(m/1_000_000,2)}M"
    elif m > 1_000:
        return f"${round(m/1_000,2)}k"
    else:
        return f"${int(m)}"


def format_token_message(name, symbol, address, price, liquidity, mcap, vol, hours_old, change_1h, change_6h, change_24h):
    return (
        f"\ud83d\udcc8 *{name}* ({symbol})\n"
        f"\ud83d\udccd `{address}`\n"
        f"\ud83d\udd52 Creat fa: {hours_old} hores\n"
        f"\ud83d\udca7 Liquidesa: ${round(liquidity):,}\n"
        f"\ud83c\udff7\ufe0f Market Cap: {format_mcap(mcap)}\n"
        f"\ud83d\udd04 Vol 24h: ${round(vol):,}\n"
        f"\ud83d\udcc8 Canvi 1h: {round(change_1h, 1)}% | 6h: {round(change_6h,1)}% | 24h: {round(change_24h,1)}%\n"
        f"\ud83d\udcb5 Preu: ${round(price, 4) if isinstance(price, float) else price}\n"
        f"\ud83d\udd17 [Birdeye Link](https://birdeye.so/token/{address}?chain=solana)"
    )