import pandas as pd
import finplot as fplt

df = pd.read_csv('cache.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
# df = df.set_index('datetime')
df = df.rename(columns={'vol':'volume'})
print(df)

# create two axes
ax = fplt.create_plot('RTS', rows=1)

# plot candle sticks
# candles = df[['open', 'close', 'high', 'low']]
candles = df[['datetime', 'open', 'close', 'high', 'low']]
fplt.candlestick_ochl(candles, ax=ax)

# overlay volume on the top plot
# volumes = df[['open','close','volume']]
volumes = df[['datetime', 'open','close','volume']]
fplt.volume_ocv(volumes, ax=ax.overlay())

fplt.show()
