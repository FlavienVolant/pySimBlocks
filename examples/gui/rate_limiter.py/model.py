from parameters_auto import *
from pySimBlocks import Model, Simulator
from pySimBlocks.blocks.operators.rate_limiter import RateLimiter
from pySimBlocks.blocks.sources.ramp import Ramp

model = Model('auto_model')

ramp = Ramp('ramp', slope=ramp_slope, start_time=ramp_start_time, offset=ramp_offset)
model.add_block(ramp)

rate_limiter = RateLimiter('rate_limiter', rising_slope=rate_limiter_rising_slope, falling_slope=rate_limiter_falling_slope, initial_output=rate_limiter_initial_output)
model.add_block(rate_limiter)

model.connect('ramp', 'out', 'rate_limiter', 'in')

simulator = Simulator(model, dt=dt)