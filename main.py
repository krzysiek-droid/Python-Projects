import ccxt_ohlc
from functions import *
from ccxt_ohlc import *
from variables import *
from price_indicators import *

# ------------------------------------ SETTINGS
# -------- SWINGS
# ------- Internal Structure
show_iswing_structure = True
ifilter_confluence: bool = False

# -- Swing Structure
show_swing_structure = True
show_swings = True
length = 20
ilength = 5
show_strong_weak = True

# -------- ORDER BLOCKS
show_internal_order_blocks = True
show_swing_order_blocks = True
number_shown_iobs = 5
number_shown_obs = 5
order_block_filter = 'Cmean'  # 'Atr' or 'Cmean'

# --------- EQH/EQL
show_eqh_eql = True
eq_len = 3  # min. 1
eq_threshold = 0.1  # min. 0, max 0.5

# --------- FAIR VALUE GAPS
fvg_show = True
fvg = True  # Calculate Fair Value Gaps
fvg_tf = ""  # Timeframe for FVGs
fvg_auto = True  # auto-threshold for FVG
fvg_extend = 1

# -------- Highs/Lows MTF
show_pdhl = False
show_pwhl = False
show_pmhl = False

# -----------------------------------------------------------------  Dataset long indicators

peaks_x_pos = find_high_pivots(dfLB['high'].values.tolist(), eq_len, eq_threshold)
troughs_x_pos = find_low_pivots(dfLB['low'].values.tolist(), eq_len, eq_threshold)


#####################################################################################################
# --------------------- MAIN LOOP ------------------------------------------------------------------
skipped_data = atr_smoothing_range if order_block_filter == "Atr" else length
for i in range(len(dfLB))[skipped_data:]:
    p_time, time = dfLB['time'][i - 1], dfLB['time'][i]
    p_open, open = dfLB['open'][i - 1], dfLB['open'][i]
    p_high, high = dfLB['high'][i - 1], dfLB['high'][i]
    p_low, low = dfLB['low'][i - 1], dfLB['low'][i]
    p_close, close = dfLB['close'][i - 1], dfLB['close'][i]
    p_volume, volume = dfLB['volume'][i - 1], dfLB['volume'][i]

    top, bottom = detect_swings(i, length, market_state)
    itop, ibottom = detect_swings(i, ilength, market_istate)

    # Pivot High
    # Check if the current high is a swing point in window of length
    if top > 0:
        variables_dict["top_cross"] = True
        variables_dict["txt_top"].append('HH' if top > variables_dict['top_y'][-1] else 'LH')

        variables_dict["top_y"].append(top)
        variables_dict["top_x"].append(i - length)
        swings['top'].append({'y': top, 'x': i - length, 'type': variables_dict['txt_top'][-1],
                              'time': dfLB['time'][i - length], 'market_state': (market_state[-2], market_state[-1])})

        variables_dict["trail_up"] = top
        variables_dict["trail_up_x"] = i - length

    if itop > 0:
        variables_dict["itop_cross"] = True

        variables_dict["itop_y"].append(itop)
        variables_dict["itop_x"].append(i - ilength)
        swings['itop'].append({'y': itop, 'x': i - ilength, 'type': 'itop', 'time': dfLB['time'][i - ilength],
                               'market state': (market_istate[-2], market_istate[-1])})

    # Trailing maximum
    if high > variables_dict["trail_up"]:
        variables_dict["trail_up"] = high
        variables_dict["trail_up_x"] = i

    variables_dict['trail_up_strength'] = 'Strong High' if variables_dict['trend'] < 0 else "Weak High"

    # Pivot low
    if bottom > 0:
        variables_dict["btm_cross"] = True
        variables_dict["txt_btm"].append('LL' if bottom < variables_dict["btm_y"][-1] else 'HL')

        variables_dict["btm_y"].append(bottom)
        variables_dict["btm_x"].append(i - length)
        swings['bot'].append({'y': bottom, 'x': i - length, 'type': variables_dict['txt_btm'][-1],
                              'time': dfLB['time'][i - length], 'market_state': (market_state[-2], market_state[-1])})

        variables_dict['trail_dn'] = bottom
        variables_dict['trail_dn_x'] = i - length

    # Check if the current high is a swing point in window of 5
    if ibottom > 0:
        variables_dict["ibtm_cross"] = True

        variables_dict["ibtm_y"].append(ibottom)
        variables_dict["ibtm_x"].append(i - ilength)
        swings['ibot'].append({'y': ibottom, 'x': i - ilength, 'type': 'ibot', 'time': dfLB['time'][i - ilength],
                               'market state': (market_istate[-2], market_istate[-1])})

    # Trailing minimum
    if low < variables_dict["trail_dn"]:
        variables_dict["trail_dn"] = low
        variables_dict["trail_dn_x"] = i
    variables_dict['trail_dn_strength'] = 'Strong Low' if variables_dict['trend'] > 0 else "Weak Low"

    # ----------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------- Pivot High BoS/CHoCH
    if ifilter_confluence:
        bull_concordant = high - max(p_close, p_open) > min(p_close, (p_close - p_low))
    else:
        bull_concordant = True

    # Detect internal bullish structure
    if cross_over(dfLB['close'][:i].tolist(), variables_dict['itop_y']) and \
            variables_dict['itop_cross'] and \
            variables_dict['top_y'][-1] != variables_dict['itop_y'][-1] and \
            bull_concordant:

        choch = False

        if variables_dict["itrend"] < 0:
            choch = True
            variables_dict["bull_ichoch_alert"] = True
        else:
            variables_dict["bull_ibos_alert"] = True

        structure = {'x_start': variables_dict['itop_x'][-1], 'x_end': i,
                     'time': dfLB['time'][variables_dict['itop_x'][-1]],
                     'level': variables_dict['itop_y'][-1], 'type': 'CHoCH' if choch else 'BoS'}

        bull_iswing_structures = bull_iswing_structures.append(structure, ignore_index=True)

        variables_dict["itop_cross"] = False
        variables_dict["itrend"] = 1

        # Internal Order Block
        ob_coord(False, i, variables_dict["itop_x"][-1], iobs)

    # Detect bullish structure
    if cross_over(dfLB['close'][:i].tolist(), variables_dict['top_y']) and variables_dict["top_cross"]:
        choch = None

        if variables_dict["trend"] < 0:
            choch = True
            variables_dict["bull_choch_alert"] = True
        else:
            variables_dict["bull_bos_alert"] = True

        structure = {'x_start': variables_dict['top_x'][-1], 'x_end': i,
                     'time': dfLB['time'][variables_dict['top_x'][-1]],
                     'level': variables_dict['top_y'][-1], 'type': 'CHoCH' if choch else 'BoS'}

        bull_swing_structures = bull_swing_structures.append(structure, ignore_index=True)
        # Order Block
        ob_coord(False, i, variables_dict['top_x'][-1], obs)

        variables_dict["top_cross"] = False
        variables_dict["trend"] = 1

    if ifilter_confluence:
        bear_concordant = (p_high - max(p_close, p_open)) < min(p_close, (p_open - p_low))
    else:
        bear_concordant = True

    # --------------------------------------------------------------------------------------
    # Detect internal bearish structure
    if cross_under(dfLB['close'][:i].tolist(), variables_dict['ibtm_y']) and \
            variables_dict['ibtm_cross'] and \
            variables_dict['btm_y'][-1] != variables_dict['ibtm_y'][-1] and \
            bear_concordant:

        choch = False

        if variables_dict['itrend'] > 0:
            choch = True
            variables_dict['bear_ichoch_alert'] = True
        else:
            variables_dict['bear_ibos_alert'] = True

        structure = {'x_start': variables_dict['ibtm_x'][-1], 'x_end': i,
                     'time': dfLB['time'][variables_dict['ibtm_x'][-1]],
                     'level': variables_dict['ibtm_y'][-1], 'type': 'CHoCH' if choch else 'BoS'}
        bear_iswing_structures = bear_iswing_structures.append(structure, ignore_index=True)

        ob_coord(True, i, variables_dict['ibtm_x'][-1], iobs)

        variables_dict['ibtm_cross'] = False
        variables_dict['itrend'] = -1

    # Detect bearish Structure
    if cross_under(dfLB['close'][:i].tolist(), variables_dict['btm_y']) and variables_dict['btm_cross']:
        choch = False

        if variables_dict['trend'] > 0:
            choch = True
            variables_dict['bear_choch_alert'] = True
        else:
            variables_dict['bear_bos_alert'] = True

        structure = {'x_start': variables_dict['btm_x'][-1], 'x_end': i,
                     'time': dfLB['time'][variables_dict['btm_x'][-1]],
                     'level': variables_dict['btm_y'][-1], 'type': 'CHoCH' if choch else 'BoS'}
        bear_swing_structures = bear_swing_structures.append(structure, ignore_index=True)

        ob_coord(True, i, variables_dict['btm_x'][-1], obs)

        variables_dict['btm_cross'] = False
        variables_dict['trend'] = -1

    # Delete internal order block box coordinates if top/bottom is broken
    filter_order_blocks(iobs, close, iobs_to_remove)

    filter_order_blocks(obs, close, obs_to_remove)

    # -------------------------------------------------------------------------------------------------------
    # ---------------------------------------- EQH/EQL
    # --------------- EQH
    if i - eq_len in peaks_x_pos:
        if len(eqhs) > 1:
            eq_top = dfLB['high'][i - eq_len]

            previous_tops = eqhs['top'].tolist()

            if max(eq_top, previous_tops[-1]) < \
                    round((min(eq_top, previous_tops[-1]) + (atr[i] * eq_threshold)), 2):
                new_eqh = {'top': eq_top, 'top_x': i - eq_len, 'time': dfLB['time'][i - eq_len]}
                real_eqhs.append(pd.DataFrame([eqhs.iloc[-1].to_dict(), new_eqh]))

                variables_dict['eqh_alert'] = True

            new_eqh = {'top': eq_top, 'top_x': i - eq_len, 'time': dfLB['time'][i - eq_len]}
            eqhs = eqhs.append(new_eqh, ignore_index=True)

        else:
            eq_top = dfLB['high'][i - eq_len]
            new_eqh = {'top': eq_top, 'top_x': i - eq_len, 'time': dfLB['time'][i - eq_len]}
            eqhs = eqhs.append(new_eqh, ignore_index=True)

    # --------------- EQL
    if i - eq_len in troughs_x_pos:
        if len(eqls) > 1:
            eq_btm = dfLB['low'][i - eq_len]
            previous_bots = eqls['bot'].tolist()

            if min(eq_btm, previous_bots[-1]) >= \
                    round((max(eq_btm, previous_bots[-1]) - (atr[i] * eq_threshold)), 2):
                new_eql = {'bot': eq_btm, 'bot_x': i - eq_len, 'time': dfLB['time'][i - eq_len]}
                real_eqls.append(pd.DataFrame([eqls.iloc[-1].to_dict(), new_eql]))

                variables_dict['eql_alert'] = True

            new_eql = {'bot': eq_btm, 'bot_x': i - eq_len, 'time': dfLB['time'][i - eq_len]}
            eqls = eqls.append(new_eql, ignore_index=True)

        else:
            eq_btm = dfLB['low'][i - eq_len]
            new_eql = {'bot': eq_btm, 'bot_x': i - eq_len, 'time': dfLB['time'][i - eq_len]}
            eqls = eqls.append(new_eql, ignore_index=True)
    # ------------------------------------------------------------------------------------------------------------------
    # -------------------------------------------- Fair Value Gaps
    bull_fvg_max, bull_fvg_min = [], []
    bear_fvg_max, bear_fvg_min = [], []
    bull_fvg_avg = None
    baer_fvg_avg = None
    bull_fvg_cnd = False
    bear_fvg_cnd = False

    if fvg_show:
        change_tf = True

        p_close, p_open, high, low, pp_high, pp_low = \
            get_ohlc(dfLB, i) if fvg_tf == '' else get_ohlc(get_data(ccxt_ohlc.symbol, fvg_tf), i)

        delta_pers.append(((p_close - p_open) / p_open) * 100)
        pers_threshold = sum([abs(_) for _ in delta_pers]) / i * 2

        threshold = 0 if not fvg_auto else (pers_threshold if change_tf else 0)

        #   --------------------------------- FVG Areas
        bull_fvg_cnd = (low > pp_high) and (p_close > pp_high) and (delta_pers[-1] > threshold) and change_tf
        bear_fvg_cnd = (high < pp_low) and (p_close < pp_low) and (-delta_pers[-1] > threshold) and change_tf

        if bull_fvg_cnd:
            new_fvg = {'left': i - 1, 'top_min': (low + pp_high) / 2, 'top_max': low,
                       'right': i + fvg_extend, 'btm_min': pp_high, 'btm_max': (low + pp_high) / 2,
                       'time': time}
            bullish_fvgs = bullish_fvgs.append(new_fvg, ignore_index=True)

        if bear_fvg_cnd:
            new_fvg = {'left': i - 1, 'top_min': (high + pp_low) / 2, 'top_max': pp_low,
                       'right': i + fvg_extend, 'btm_min': high, 'btm_max': (high + pp_low) / 2,
                       'time': time}
            bearish_fvgs = bearish_fvgs.append(new_fvg, ignore_index=True)

    fvgs_broken = []
    for row in bullish_fvgs.iterrows():
        if low < row[1]['btm_min']:
            fvgs_broken.append(row[0])
    bullish_fvgs.drop(fvgs_broken, inplace=True)

    fvgs_broken = []
    for row in bearish_fvgs.iterrows():
        if high >= row[1]['top_max']:
            fvgs_broken.append(row[0])
    bearish_fvgs.drop(fvgs_broken, inplace=True)

#   ------------------------------------------------------------------------------------------------------
#   ----------------- PREMIUM/DISCOUNT AREAS
# --- PREMIUM
premium_zone = {'left': max(variables_dict['top_x'][-1], variables_dict['btm_x'][-1]),
                'top': variables_dict['trail_up'],
                'right': len(dfLB) - 1,
                'btm': round((0.95 * variables_dict['trail_up']) + (0.05 * variables_dict['trail_dn']), 2)}
premium_area = premium_area.append(premium_zone, ignore_index=True)
# --- EQ
eq_zone = {'left': max(variables_dict['top_x'][-1], variables_dict['btm_x'][-1]),
           'top': round((0.525 * variables_dict['trail_up']) + (0.475 * variables_dict['trail_dn']), 2),
           'right': len(dfLB) - 1,
           'btm': round((0.525 * variables_dict['trail_dn']) + (0.475 * variables_dict['trail_up']), 2)}
eq_area = eq_area.append(eq_zone, ignore_index=True)
# --- DISCOUNT
discount_zone = {'left': max(variables_dict['top_x'][-1], variables_dict['btm_x'][-1]),
                 'top': round((0.95 * variables_dict['trail_dn']) + (0.05 * variables_dict['trail_up']), 2),
                 'right': len(dfLB) - 1,
                 'btm': variables_dict['trail_dn']}
discount_area = discount_area.append(discount_zone, ignore_index=True)

# ------------------------------------------------POST LOOP CODE
print("-------------------------------------------------------------------- OUTPUT ---------------------")

# ------------------ SWING STRUCTURES
if show_iswing_structure:
    print(f"Bullish iSwing Structures: \n {bull_iswing_structures}")
    print()
    print(f"Bearish iSwing Structures: \n {bear_iswing_structures}")

if show_swing_structure:
    print(f'Bullish Swing Structures: \n {bull_swing_structures}')
    print()
    print(f"Bearish Swing Structures: \n {bear_swing_structures}")

# ------- Show swing points
if show_swings:
    print(f"TOP SWINGS")
    for swing in swings['top']:
        print(swing)

    print()
    print(f"BOTTOM SWINGS")
    for swing in swings['bot']:
        print(swing)

    print()
    print(f"ITop SWINGS (last)")
    for swing in swings['itop']:
        print(swing)

    print()
    print(f"IBot SWINGS (last )")
    for swing in swings['ibot']:
        print(swing)

    # ----- Show Strong/Weak High/Low (most recent!)
if show_strong_weak:
    print()
    print(f"Most recent High/Low (trailing High/Low) with strength:")
    print(f"High -> {variables_dict['trail_up']} - {variables_dict['trail_up_strength']}")
    print(f"Low -> {variables_dict['trail_dn']} - {variables_dict['trail_dn_strength']}")

# --------------------------------------- ORDER BLOCKS
if show_internal_order_blocks:
    print()
    print(f"Internal Order Blocks: ")
    iobs = iobs.drop(index=set(iobs_to_remove)).reset_index()
    print(iobs.tail(number_shown_iobs))
if show_swing_order_blocks:
    print()
    print(f"Order Blocks:")
    obs = obs.drop(index=set(obs_to_remove)).reset_index()
    print(obs.tail(number_shown_iobs))

# -------------------------------------- EQH/EQL
if show_eqh_eql:
    print()
    print(f"Real EQH (Lines) (filtered)")
    for real_eqh in real_eqhs:
        print(real_eqh.to_dict())
    # print(eqhs)
    print()
    print(f"Real EQL (Lines) (filtered)")
    for real_eql in real_eqls:
        print(real_eql.to_dict())
    # print(eqls)

# ------------------------------------- Fair Value Gaps
if fvg_show:
    print()
    print(f"Bullish Fair Gaps Value")
    print(bullish_fvgs)

    print()
    print(f"Barish Fair Value Gaps")
    print(bearish_fvgs)

# --------------------------- Previous day/week high/lows
if show_pdhl or show_pwhl or show_pmhl:
    print()
    print("PREVIOUS DAY/WEAK HIGH/LOWS:")
    if show_pdhl:
        show_previous_hl('1d')
    if show_pwhl:
        show_previous_hl('1w')
    if show_pmhl:
        show_previous_hl('1M')

# -------------------------- Show Premium/Discount zones
print()
print(f"Premium/Equlibrium/Discount areas start at: "
      f"{dfLB['time'][max(variables_dict['top_x'][-1], variables_dict['btm_x'][-1])]}")
print(f"PREMIUM AREA: \n {premium_area}")
print(f"\n EQULIBRIUM AREA: \n {eq_area}")
print(f"\n DISCOUNT AREA: \n {discount_area}")
