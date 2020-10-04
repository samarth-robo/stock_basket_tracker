from app import start_app
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


class Stock(object):
  def __init__(self, name) -> None:
    self.name = name
    self.vis = True
    self.prices = []
    self.times = []
    self.vis_kwargs = {'mode': 'lines+markers',
                       'line': {'width': 1, 'dash': 'dash'}}

  def get_data(self, start_year=-1):
    print('Getting {:s} data'.format(self.name))
    self.times = np.asarray(list(range(10)))
    self.prices = np.random.uniform(0, 100, len(self.times))


class BasketTracker(object):
  def __init__(self, filename, start_year=1990) -> None:
    self.start_year = start_year
    
    with open(filename, 'r') as f:
      d = json.load(f)

    names = []
    fracs = []
    for n,f in d.items():
      names.append(n)
      fracs.append(float(f))
    if abs(np.sum(fracs) - 1.0) > 0.1:
      print('Normalizing basket fractions')
    self.fracs = np.asarray(fracs) / np.sum(fracs)
    self.stocks = [Stock(n) for n in names]
    for s in self.stocks:
      s.get_data(self.start_year)

    self.fig = go.Figure()

  
  def _calc_basket(self):
    b = Stock('basket')
    start_time = np.max([s.times[0]  for s in self.stocks])
    end_time   = np.min([s.times[-1] for s in self.stocks])
    b.times = np.asarray(list(range(start_time, end_time+1)))
    ps = []
    for s, f in zip(self.stocks, self.fracs):
      i0 = np.searchsorted(s.times, start_time)
      assert(i0 > 0 or start_time==s.times[0])
      i1 = np.searchsorted(s.times, end_time)
      assert(i1 < len(s.times))
      ps.append(f * s.prices[i0:i1+1])
    b.prices = np.sum(np.vstack(ps), axis=0)
    b.vis_kwargs['line']['width'] = 4
    b.vis_kwargs['line'].pop('dash')
    return b

  
  def show(self):
    self.fig.data = []
    for s in self.stocks + [self._calc_basket()]:
      if not s.vis:
        continue
      self.fig.add_trace(go.Scatter(x=s.times, y=s.prices, name=s.name,
                                    **s.vis_kwargs))
    start_app(self.fig)


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--ticker_names_file', required=True)
  parser.add_argument('--start_year', type=int, default=1990)
  args = parser.parse_args()

  bt = BasketTracker(args.ticker_names_file, args.start_year)
  bt.show()
