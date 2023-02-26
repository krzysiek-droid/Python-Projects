import pandas as pd
import numpy as np

market_state = []
market_istate = []
delta_pers = []

# variables
variables_dict = {
    "trend": 0,
    "itrend": 0,
    "top_y": [0, 0],
    "top_x": [0, 0],
    "btm_y": [0, 0],
    "btm_x": [0, 0],
    "itop_y": [0, 0],
    "itop_x": [0, 0],
    "ibtm_y": [0, 0],
    "ibtm_x": [0, 0],
    "trail_up": 0,
    "trail_up_strength": None,
    "trail_dn": 0,
    'trail_dn_strength': None,
    "trail_up_x": 0,
    "trail_dn_x": 0,
    "top_cross": True,
    "btm_cross": True,
    "itop_cross": False,
    "ibtm_cross": True,
    "txt_top": [""],
    "txt_btm": [""],
    "bull_choch_alert": False,
    "bull_bos_alert": False,
    "bear_choch_alert": False,
    "bear_bos_alert": False,
    "bull_ichoch_alert": False,
    "bull_ibos_alert": False,
    "bear_ichoch_alert": False,
    "bear_ibos_alert": False,
    "bull_iob_break": False,
    "bear_iob_break": False,
    "bull_ob_break": False,
    "bear_ob_break": False,
    "eqh_alert": False,
    "eql_alert": False,

}

iobs = pd.DataFrame(columns=['top', 'btm',
                             'left', 'type'])

iobs_to_remove = []

obs = pd.DataFrame(columns=['top', 'btm',
                            'left', 'type'])
obs_to_remove = []

swings = {
    'top': [],
    'bot': [],
    'itop': [],
    'ibot': []
}

bull_swing_structures = pd.DataFrame(columns=['x_start', 'x_end',
                                        'time', 'level', 'type'])
bear_swing_structures = pd.DataFrame(columns=['x_start', 'x_end',
                                        'time', 'level', 'type'])
bull_iswing_structures = pd.DataFrame(columns=['x_start', 'x_end',
                                        'time', 'level', 'type'])
bear_iswing_structures = pd.DataFrame(columns=['x_start', 'x_end',
                                        'time', 'level', 'type'])

eqhs = pd.DataFrame(columns=['top', 'top_x', 'time'])
real_eqhs = []

eqls = pd.DataFrame(columns=['bot', 'bot_x', 'time'])
real_eqls = []

bullish_fvgs = pd.DataFrame(columns=['left', 'top_min', 'top_max',
                                     'right', 'btm_min', 'btm_max', 'time'])
bearish_fvgs = pd.DataFrame(columns=['left', 'top_min', 'top_max',
                                     'right', 'btm_min', 'btm_max', 'time'])

premium_area = pd.DataFrame(columns=['left', 'top', 'right', 'btm'])
eq_area = pd.DataFrame(columns=['left', 'top', 'right', 'btm'])
discount_area = pd.DataFrame(columns=['left', 'top', 'right', 'btm'])