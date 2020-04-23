import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import datetime
import time
from scipy.special import comb


plt.style.use('default')
plt.style.use('default')

## Import data
data = np.load('data.npy')
trading_dates = np.load('trading_dates.npy')

## Visual constants
minute_interval = 90
second_interval = minute_interval * 60
day_open = 60 * 60 * 9.5
trading_day_seconds = int((60 * 60 * 6.5))
trading_day_minutes = int(trading_day_seconds / 60)
times = [time.strftime('%I:%M', time.gmtime(i + day_open)) for i in range(trading_day_seconds + 1)
             if i % second_interval == 0]
time_ids = [i for i in range(trading_day_seconds + 1) if i % second_interval == 0]
loc_of_real = ['']
loc_of_random = ['']
date = ['']

## Math constants
expected = (trading_day_seconds) ** 0.5  # expected travel from the start, wiki if unfamiliar
show_every = 60
expected_volatility = 0.006  # the sd of the minute bar steps is set by a gamma about 0.6%
shape = 7
expected_open = 0.004

## Misc constants
N = len(data)

prev_ns = list()  # resets after each game

# size = (18, 6)  # horizontal
size = (8, 11.5)  # vertical

Y = 'Yes'


def main():

    continue_cond = True
    correct = 0
    attempted = 0

    print()
    print("""Do you think you can tell the difference between a random walk and a day of the S&P 500?
Play this game to find out!""")
    print()

    c1 = True
    while c1:
        begin = input("""Enter 'y' to begin...\n""")
        if begin == 'y':
            c1 = False

    while continue_cond:

        side_by_side()

        # print('Is the the S&P 500 on the left or the right?')  # horizontal
        print('Is the the S&P 500 on the top or the bottom?')  # vertical

        # believed_loc = input("""Enter 'left' or 'right'.\n""")  # horizontal
        c3 = True
        while c3:
            # print('The day is ', date[0], '.', sep='')  # temporary

            believed_loc = input("""Enter 't' for top, 'b' for bottom, or 'q' to quit.\n\n\n\n\n\n""")

            if believed_loc  == loc_of_real[0][0]:  # final [0] for first letter 't'
                print('Correct :)')
                correct += 1
                attempted += 1
                c3 = False
            elif believed_loc == loc_of_random[0][0]:  # final [0] for first letter 't'
                print('Incorrect :(')
                attempted += 1
                c3 = False
            elif believed_loc == 'q':
                print('You successfully quit the game.')
                c3 = False
                continue_cond = False

        print('The S&P 500 was on the ', loc_of_real[0], ', the day was ', date[0], '.', sep='')
        print('The random walk was on the ', loc_of_random[0], '.', sep='')

        time.sleep(1.5)

        print()
        print('You\'ve gotten {} out of {} correct, or '.format(correct, attempted),
              '{0:.1%}'.format(correct / attempted), '!', sep='')

        p = p_value(n_correct=correct, n_trials=attempted)
        print('The probability of performing at least this well by random guessing is:',
              "{0:.2%}".format(p))
        if p < 0.05:
            print('This means that, at the 5% significance level, you CAN tell the difference. AMAZING!')

        else:
            print('This means that, at the 5% significance level, you cannot tell the difference, SAD!')
            # insert probability of a false negative here
        print()

        time.sleep(1.5)

        if len(prev_ns) >= N:
            print('You\'ve gone through all our data! The game must end.')
            continue_cond = False

        if continue_cond:
            print('~~~~~~~~~~~~~~', end='')
            print(' NEW ROUND ', end='')
            print('~~~~~~~~~~~~~~')
            print()



## FUNCTIONS
def get_random():
    volatility = np.random.gamma(shape=shape, scale=expected_volatility / shape)

    steps = np.random.randn(trading_day_seconds)  # changed + 1
    steps *= volatility

    prices = np.cumsum(steps)
    prices /= expected  # everything is divided by the expected distance away, set by the sqr root
    # of the number of steps

    starting_price = expected_open * np.random.randn()  # normal with 0.4% standard deviation
    prices += starting_price  # return

    prices = prices[::show_every]
    x = np.arange(trading_day_seconds)[::show_every]  # return  # changed + 1

    return x, prices


def plot_stock(axis, x, y):
    if y[-1] < 0:
        color = 'xkcd:red'
    else:
        color = 'xkcd:green'

    axis.grid(alpha=0.4)
    axis.plot([0], [0])
    axis.plot(x, y, color=color, alpha=0.9)

    axis.yaxis.set_major_formatter(PercentFormatter(1))
    axis.set_xlim(0, x[-1])

    lims = axis.get_ylim()
    axis.set_ylim(lims)
    axis.fill_between(x, np.full(len(x), lims[0]), y, alpha=0.1, color=color)
    axis.set_xticks(time_ids)
    axis.set_xticklabels(times)


def get_side(num):
    if num == 0:
        return 'left'
    elif num == 1:
        return 'right'


def get_side_vertical(num):
    if num == 0:
        return 'top'
    elif num == 1:
        return 'bottom'


def side_by_side():
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=size)
    fig.suptitle('One is a random walk, the other is an\nactual day in the stock market...',
                 fontsize=20)
    # 13.5, 4.5
    # randomly put the random on the left or right, and the real in the other spot
    random_idx = np.random.randint(2)
    real_idx = 1 - random_idx

    random_x, random_y = get_random()
    plot_stock(axes[random_idx], random_x, random_y)

    real_x, real_y = get_real()
    plot_stock(axes[real_idx], real_x, real_y)

    loc_of_random[0] = get_side_vertical(random_idx)
    loc_of_real[0] = get_side_vertical(real_idx)

    plt.savefig('hack.png', dpi=180)





def p_value(n_correct, n_trials):
    # the number of selections to choose from is n_trials * 2 and
    # n_trials are chosen
    possible_combs = comb(n_trials * 2, n_trials)

    possible_as_or_greater_combs = 0
    for n in range(n_correct, n_trials + 1):
        possible_as_or_greater_combs += comb(n_trials, n) * comb(n_trials, n_trials - n)

    return possible_as_or_greater_combs / possible_combs


def get_real():
    x = np.arange(trading_day_seconds, step=60)

    while True:  # set the date_n
        date_n = np.random.randint(N)
        if len(prev_ns) >= N:
            break
        if date_n not in prev_ns:
            break
    prev_ns.append(date_n)

    y = data[date_n]
    date[0] = datetime.datetime.strptime(trading_dates[date_n], '%Y.%m.%d').strftime("%A, %B %-d, %Y")
    return x, y


if __name__ == '__main__':
    main()
