import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_stablecoin_vs_total_roc(total_df, usdt_d_df, usdc_d_df, roc_len=30):
    """
    Calculates and compares the Rate of Change (ROC) of the total crypto market
    cap against the inverted ROC of major stablecoin dominance.
    """
    df = pd.concat([
        total_df['close'].rename('total'),
        usdt_d_df['close'].rename('usdt_d'),
        usdc_d_df['close'].rename('usdc_d')
    ], axis=1).dropna()
    df['roc_total'] = (df['total'] - df['total'].shift(roc_len)) / df['total'].shift(roc_len) * 100
    df['roc_usdt'] = (df['usdt_d'] - df['usdt_d'].shift(roc_len)) / df['usdt_d'].shift(roc_len) * 100
    df['roc_usdc'] = (df['usdc_d'] - df['usdc_d'].shift(roc_len)) / df['usdc_d'].shift(roc_len) * 100
    df['roc_stable_inv'] = -((df['roc_usdt'] + df['roc_usdc']) / 2)
    return df[['roc_total', 'roc_stable_inv']].dropna()


def calculate_altcoin_season_index_v1(total3_df, btcd_df, ma_length=30):
    """
    Calculates the original Altcoin Season Index (ASI) based on the momentum
    spread between TOTAL3 and BTC.D.
    """
    df = pd.concat([
        total3_df['close'].rename('total3'),
        btcd_df['close'].rename('btcd')
    ], axis=1).dropna()
    total3_roc = df['total3'].pct_change(1) * 100
    btcd_roc = df['btcd'].pct_change(1) * 100
    df['asi_value'] = total3_roc - btcd_roc
    df['signal_line'] = df['asi_value'].rolling(window=ma_length).mean()
    return df[['asi_value', 'signal_line']].dropna()


def calculate_traffic_light(total_df, len_fast=21, len_medium=50, len_slow=200):
    """
    Determines the macro trend regime based on the alignment of key moving averages.
    """
    df = total_df.copy()
    df[f'EMA_{len_fast}'] = df.ta.ema(length=len_fast)
    df[f'SMA_{len_medium}'] = df.ta.sma(length=len_medium)
    df[f'SMA_{len_slow}'] = df.ta.sma(length=len_slow)
    df.dropna(inplace=True)
    conditions = [
        (df['close'] > df[f'EMA_{len_fast}']) & 
        (df[f'EMA_{len_fast}'] > df[f'SMA_{len_medium}']) & 
        (df[f'SMA_{len_medium}'] > df[f'SMA_{len_slow}']),
        (df['close'] < df[f'SMA_{len_slow}'])
    ]
    colors = ['rgba(87, 228, 92, 0.25)', 'rgba(255, 82, 82, 0.25)']
    default_color = 'rgba(255, 235, 59, 0.25)'
    df['regime_color'] = np.select(conditions, colors, default=default_color)
    return df


def calculate_ad_line(data_dict):
    """
    Calculates the Advance/Decline line from a dictionary of asset DataFrames.
    """
    all_changes = []
    for symbol, df in data_dict.items():
        price_diff = df['close'].diff()
        score = np.sign(price_diff).rename(symbol)
        all_changes.append(score)
    combined_df = pd.concat(all_changes, axis=1)
    daily_ad_score = combined_df.sum(axis=1, skipna=True)
    ad_line = daily_ad_score.cumsum()
    result_df = pd.DataFrame({
        'daily_ad_score': daily_ad_score,
        'ad_line': ad_line
    })
    return result_df.dropna()


def calculate_assets_above_ma(data_dict, ma_length):
    """
    Calculates the percentage of assets trading above a specified SMA.
    """
    above_ma_list = []
    for symbol, df in data_dict.items():
        if len(df) > ma_length:
            sma = df.ta.sma(length=ma_length)
            is_above = (df['close'] > sma).rename(symbol)
            above_ma_list.append(is_above)
    combined_df = pd.concat(above_ma_list, axis=1)
    percentage_above = (combined_df.sum(axis=1) / len(combined_df.columns)) * 100
    return percentage_above.dropna()


def calculate_distance_from_ma(data_dict, ma_length):
    """
    For each asset, calculates the percentage distance of its latest close price
    from a specified simple moving average (SMA).
    """
    distances = {}
    for symbol, df in data_dict.items():
        if len(df) > ma_length:
            sma = df.ta.sma(length=ma_length)
            latest_close = df['close'].iloc[-1]
            latest_sma = sma.iloc[-1]
            if latest_sma > 0:
                distance = ((latest_close - latest_sma) / latest_sma) * 100
                distances[symbol] = distance
    return pd.Series(distances).sort_values()

def calculate_market_character(data_dict, lookback_period=30):
    """
    For each asset, calculates its 30-day momentum (ROC) and 30-day
    realized volatility to position it within the Market Character Quadrant.

    Args:
        data_dict (dict): A dictionary of asset DataFrames.
        lookback_period (int): The lookback period for ROC and volatility.

    Returns:
        pd.DataFrame: A DataFrame with columns for 'momentum' and 'volatility',
                      indexed by the asset symbol.
    """
    market_character_data = []
    
    for symbol, df in data_dict.items():
        if len(df) > lookback_period:
            # Calculate 30-Day Rate of Change (Momentum)
            roc = (df['close'].iloc[-1] - df['close'].iloc[-1 - lookback_period]) / df['close'].iloc[-1 - lookback_period] * 100
            
            # Calculate 30-Day Realized Volatility
            daily_returns = df['close'].pct_change()
            volatility = daily_returns.rolling(window=lookback_period).std().iloc[-1] * np.sqrt(365) # Annualized
            
            if pd.notna(roc) and pd.notna(volatility):
                market_character_data.append({
                    'symbol': symbol,
                    'momentum': roc,
                    'volatility': volatility
                })
                
    return pd.DataFrame(market_character_data).set_index('symbol')

def calculate_regime_scatter_data(ad_data_dict, total_df, lookback_period=30):
    """
    Calculates the rolling performance (ROC) for a meme coin index and the
    total market cap, providing the data needed for the regime scatter plot.

    Args:
        ad_data_dict (dict): The dictionary of asset data from the A/D line database.
        total_df (pd.DataFrame): DataFrame with close prices for TOTAL.
        lookback_period (int): The rolling window for the performance calculation.

    Returns:
        pd.DataFrame: A DataFrame with 'meme_performance' and 'total_performance' columns.
    """
    # --- Create Meme Index ---
    meme_coin_basket = ['DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT', 'BONKUSDT', 'WIFUSDT', 'FLOKIUSDT', "SPXUSDT", "PUMPUSDT", "BUSD", "BRETTUSDT", "MOGUSDT", "REKTCUSD", "SNEKUSD", "TURBOUSDT", "TOSHIUSD", "POPCATUSDT", "FARTCOINUSD"]
    meme_data = {k: v for k, v in ad_data_dict.items() if k in meme_coin_basket}
    if not meme_data:
        return pd.DataFrame()

    all_returns = pd.concat(
        [df['close'].pct_change().rename(symbol) for symbol, df in meme_data.items()],
        axis=1
    )
    average_daily_return = all_returns.mean(axis=1)
    meme_index = (1 + average_daily_return).cumprod().fillna(1)

    # --- Calculate rolling performance for both ---
    meme_performance = (meme_index / meme_index.shift(lookback_period) - 1) * 100
    total_performance = (total_df['close'] / total_df['close'].shift(lookback_period) - 1) * 100
    
    # --- Combine into a single DataFrame ---
    df = pd.concat([
        meme_performance.rename('meme_performance'),
        total_performance.rename('total_performance')
    ], axis=1).dropna()
    
    return df

def calculate_eth_breadth_wave(data_dict, benchmark_df, lookback_period=30):
    """
    Calculates the breadth of the market relative to a benchmark (ETH) by
    grouping assets into performance bands over time, returning percentages.
    """
    benchmark_roc = benchmark_df['close'].pct_change(periods=lookback_period) * 100
    
    all_asset_roc = pd.concat(
        [df['close'].pct_change(periods=lookback_period).rename(symbol) * 100
         for symbol, df in data_dict.items()],
        axis=1
    )
    
    relative_performance_df = all_asset_roc.subtract(benchmark_roc, axis=0)
    
    bands = {
        "Strongly Outperforming (>+20%)": (relative_performance_df > 20),
        "Outperforming (0% to 20%)": (relative_performance_df >= 0) & (relative_performance_df <= 20),
        "Underperforming (-20% to 0%)": (relative_performance_df < 0) & (relative_performance_df >= -20),
        "Strongly Underperforming (<-20%)": (relative_performance_df < -20)
    }
    
    # Count the number of assets in each band
    breadth_wave_df = pd.concat(
        [df.sum(axis=1).rename(name) for name, df in bands.items()],
        axis=1
    )
    
    # --- NEW: Convert counts to percentages ---
    # Calculate the total number of assets with valid data for each day
    total_assets_per_day = breadth_wave_df.sum(axis=1)
    
    # Divide the count in each band by the daily total to get the percentage
    # We use .div() and specify axis=0 to divide each column by the total_assets_per_day series
    percentage_df = breadth_wave_df.div(total_assets_per_day, axis=0) * 100
    
    return percentage_df.dropna()

def calculate_official_altcoin_season_index(majors_data, benchmark_df, btcd_df, lookback_period=90, vol_ma_period=20, normalization_window=365, smoothing_period=14):
    """
    Calculates the comprehensive "Official" Altcoin Season Index on a 0-100 scale,
    using the Z-score methodology with a 50/25/25 weighting.
    """
    # --- Internal Calculation for Price Breadth ---
    outperforming_assets = []
    for symbol, df in majors_data.items():
        if 'BTC' in symbol:
            continue
        temp_df = pd.concat([df['close'].rename('asset'), benchmark_df['close'].rename('benchmark')], axis=1)
        roc_df = temp_df.pct_change(periods=lookback_period)
        is_outperforming = (roc_df['asset'] > roc_df['benchmark']).rename(symbol)
        outperforming_assets.append(is_outperforming)
    price_breadth = (pd.concat(outperforming_assets, axis=1).sum(axis=1) / len(outperforming_assets)) * 100

    # --- Internal Calculation for Volume Breadth ---
    outperformance_volumes = []
    for symbol, df in majors_data.items():
        if 'BTC' in symbol:
            continue
        temp_df = pd.concat([
            df['close'].rename('asset_close'), df['volume'].rename('asset_volume'),
            benchmark_df['close'].rename('benchmark_close')
        ], axis=1).dropna()
        asset_roc = temp_df['asset_close'].pct_change(periods=lookback_period)
        benchmark_roc = temp_df['benchmark_close'].pct_change(periods=lookback_period)
        asset_vol_ma = temp_df['asset_volume'].rolling(window=vol_ma_period).mean()
        volume_if_outperforming = np.where(asset_roc > benchmark_roc, asset_vol_ma, 0)
        outperformance_volumes.append(pd.Series(volume_if_outperforming, index=temp_df.index).rename(symbol))
    volume_breadth = pd.concat(outperformance_volumes, axis=1).sum(axis=1)

    # --- Component 3: BTC Dominance Momentum ---
    btcd_momentum = btcd_df['close'].pct_change(periods=lookback_period) * 100

    # --- Combine and Align All Raw Components ---
    combined_df = pd.concat([price_breadth, volume_breadth, btcd_momentum], axis=1).dropna()
    combined_df.columns = ['price_breadth', 'volume_breadth', 'btcd_momentum']

    # --- Normalization using Z-scores ---
    combined_df['price_zscore'] = (combined_df['price_breadth'] - combined_df['price_breadth'].rolling(window=normalization_window).mean()) / combined_df['price_breadth'].rolling(window=normalization_window).std()
    combined_df['volume_zscore'] = (combined_df['volume_breadth'] - combined_df['volume_breadth'].rolling(window=normalization_window).mean()) / combined_df['volume_breadth'].rolling(window=normalization_window).std()
    combined_df['btcd_zscore'] = -((combined_df['btcd_momentum'] - combined_df['btcd_momentum'].rolling(window=normalization_window).mean()) / combined_df['btcd_momentum'].rolling(window=normalization_window).std())

    # --- Combine Z-scores with 50/25/25 weights ---
    combined_df['final_zscore'] = (combined_df['price_zscore'] * 0.50) + (combined_df['volume_zscore'] * 0.25) + (combined_df['btcd_zscore'] * 0.25)
    
    # --- Convert to 0-100 scale and smooth ---
    final_index = 100 / (1 + np.exp(-combined_df['final_zscore']))
    smoothed_index = final_index.rolling(window=smoothing_period).mean()

    return pd.DataFrame({'altcoin_season_index': smoothed_index}).dropna()
