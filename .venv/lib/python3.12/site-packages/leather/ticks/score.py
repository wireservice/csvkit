from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from math import isclose

from leather.ticks.base import Ticker

# Shorthand
ZERO = Decimal('0')
TEN = Decimal('10')

#: Normalized intervals to be tested for ticks
INTERVALS = [
    Decimal('0.1'),
    Decimal('0.15'),
    Decimal('0.2'),
    Decimal('0.25'),
    Decimal('0.5'),
    Decimal('1.0')
]

#: The default number of ticks to produce
DEFAULT_TICKS = 5

#: The minimum length of a viable tick sequence
MIN_TICK_COUNT = 4

#: The maximum length of a viable tick sequence
MAX_TICK_COUNT = 10

#: Most preferred tick intervals
BEST_INTERVALS = [Decimal('0.1'), Decimal('1.0')]

#: Least preferred tick intervals
WORST_INTERVALS = [Decimal('0.15')]


class ScoreTicker(Ticker):
    """
    Attempt to find an optimal series of ticks by generating many possible
    sequences and scoring them based on several criteria. Only the best
    tick sequence is returned.

    Based an algorithm described by Austin Clemens:
    http://austinclemens.com/blog/2016/01/09/an-algorithm-for-creating-a-graphs-axes/

    See :meth:`.ScoreTicker.score` for scoring implementation.

    :param domain_min:
        Minimum value of the data series.
    :param domain_max:
        Maximum value of the data series.
    """
    def __init__(self, domain_min, domain_max):
        self._domain_min = domain_min
        self._domain_max = domain_max

        self._ticks = self._find_ticks()

        self._min = self._ticks[0]
        self._max = self._ticks[-1]

    @property
    def ticks(self):
        return self._ticks

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    def _find_ticks(self):
        """
        Implements the tick-finding algorithm.
        """
        force_zero = self._domain_min < ZERO and self._domain_max > ZERO

        interval_guess = abs(self._domain_max - self._domain_min) / (DEFAULT_TICKS - 1)
        magnitude = interval_guess.log10().to_integral_exact(rounding=ROUND_CEILING)

        candidate_intervals = []

        for interval in INTERVALS:
            candidate_intervals.append((interval, interval * pow(TEN, magnitude)))
            candidate_intervals.append((interval, interval * pow(TEN, magnitude - 1)))
            candidate_intervals.append((interval, interval * pow(TEN, magnitude + 1)))

        candidate_ticks = []

        for base_interval, interval in candidate_intervals:
            ticks = []

            if force_zero:
                min_steps = (abs(self._domain_min) / interval).to_integral_exact(rounding=ROUND_CEILING)
                ticks.append(
                    self._round_tick(-min_steps * interval)
                )
            else:
                ticks.append(
                    self._round_tick((self._domain_min / interval).to_integral_exact(rounding=ROUND_FLOOR) * interval)
                )

            tick_num = 1

            while ticks[tick_num - 1] < self._domain_max:
                t = self._round_tick(ticks[0] + (interval * tick_num))

                ticks.append(t)
                tick_num += 1

            # Throw out sequences that are too short or too long
            if len(ticks) < MIN_TICK_COUNT or len(ticks) > MAX_TICK_COUNT:
                continue

            candidate_ticks.append({
                'base_interval': base_interval,
                'interval': interval,
                'ticks': ticks,
                'score': self._score(base_interval, interval, ticks)
            })

        # Order by best score, using number of ticks as a tie-breaker
        best = sorted(candidate_ticks, key=lambda c: (c['score']['total'], len(c['ticks'])))

        return best[0]['ticks']

    def _score(self, base_interval, interval, ticks):
        """
        Score a given tick sequence based on several criteria. This method returns
        discrete scoring components for easier debugging.
        """
        s = {
            'pct_waste': 0,
            'interval_penalty': 0,
            'len_penalty': 0,
            'total': 0
        }

        # Penalty for wasted scale space
        waste = (self._domain_min - ticks[0]) + (ticks[-1] - self._domain_max)
        pct_waste = waste / (self._domain_max - self._domain_min)

        s['pct_waste'] = pow(10, pct_waste)

        # Penalty for choosing less optimal tick intervals
        if base_interval in BEST_INTERVALS:
            pass
        elif base_interval in WORST_INTERVALS:
            s['interval_penalty'] = 2
        else:
            s['interval_penalty'] = 1

        # Penalty for too many ticks
        if len(ticks) > 5:
            s['len_penalty'] = (len(ticks) - 5)

        s['total'] = s['pct_waste'] + s['interval_penalty'] + s['len_penalty']

        return s

    def _round_tick(self, t):
        """
        Round a tick to 0-3 decimal places, if the remaining digits do not
        appear to be significant.
        """
        for r in range(0, 4):
            exp = pow(Decimal(10), Decimal(-r))
            quantized = t.quantize(exp)

            if isclose(t, quantized):
                return quantized

        return t
