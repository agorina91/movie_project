import pytest
import requests
import time
from bs4 import BeautifulSoup as BS
import pandas as pd
import numpy as np
from tabulate import tabulate

import plotly.express as px


def find_quantile_fraction(found_group_offset, total, target_votes, cum_freq_prior, l: list, group_midpoints: list,
                           class_length):
    """
    Given a group_offset containing the percentile, do a straight-line interpolation to get
    the fractional quantile point.
    :param found_group_offset:
    :param total:
    :param target_votes:
    :param cum_freq_prior:
    :param l:
    :param group_midpoints:
    :param class_length
    :return:
    """
    lower_class_boundary = group_midpoints[found_group_offset] - 0.5
    median_frac = lower_class_boundary + ((target_votes - cum_freq_prior) / l[found_group_offset]) * class_length
    return median_frac


def find_x_percent_index(percentile: int, l: list, group_midpoints: list):
    """
    Finds the index in the list account for percentile percentage of the data
    choses the index bin containing the percentile
    :param percentile: an integer between 0 & 100
    :param l: the list of values (in order). The first is at the zeroth percentile
    :param group_midpoints - the names of the groups
    :return: the group_midpoint value containing the percentile value
    """

    total = sum(l)
    stop_point = (percentile / 100) * total

    curr_total = 0
    prev_total = 0
    i = 0
    for v in l:
        prev_total = curr_total
        curr_total += l[i]
        if curr_total >= stop_point:
            median = find_quantile_fraction(i, total, stop_point, prev_total, l, group_midpoints,
                                            group_midpoints[1] - group_midpoints[0])
            return median

        i += 1
    # This should never happen, but if it does return the last group
    return group_midpoints(len(l) - 1)


def test_find_x_percent_index():
    vals = [2, 7, 8, 4]
    groups = [51, 56, 61, 66]

    median = find_x_percent_index(50, vals, groups)
    lower = find_x_percent_index(25, vals, groups)
    upper = find_x_percent_index(75, vals, groups)

    print(f"median: {median}, lower: {lower} upper: {upper}")
    assert median == pytest.approx(61.4375, 0.001)
    assert lower == pytest.approx(57.8214, 0.001)
    assert upper == pytest.approx(64.71875, 0.001)


def skewness_calc(x):
    """
    Calculates Bowley Skewness using quantiles for grouped data
    :param x: the data series
    :return:
    """
    # The ten ordinal value votes are in offsets 1 thru 10
    votes = x[1:11]

    # Calculate the three quantiles at 50%, 25% & 75% percentiles, respectively
    median = find_x_percent_index(50, votes, range(1, 11))
    lower = find_x_percent_index(25, votes, range(1, 11))
    upper = find_x_percent_index(75, votes, range(1, 11))

    # print(f"lower: {lower} median: {median} upper: {upper}")

    # Check denominator == 0, to avoid divide by zero
    if (upper - lower) == 0:
        return 0
    else:
        skewness = ((median - lower) - (upper - median)) / (upper - lower)

    return pd.Series([lower, median, upper, skewness])


def add_skewness(user_df):
    user_df = user_df.drop(['mean', 'median'], axis=1)

    # user_df['skewness'] = user_df.apply(skewness_calc, axis=1)
    user_df[['lower', 'median', 'upper', 'skewness']] = user_df.apply(skewness_calc, axis=1)
    return user_df


def make_skewness():
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 100)
    udf = pd.read_csv('user_movie_table.csv', sep='\t')
    # print(udf)
    skewed = add_skewness(udf)

    # print(tabulate(skewed, headers='keys', tablefmt='psql'))
    print(tabulate(skewed, headers='keys', tablefmt='psql'))

    dir_path = "/Users/rebjl/PycharmProjects/movie_project/"
    skewed.to_csv(dir_path + "skewed.csv", sep="\t")


def bin_skewness():
    """
    Bucket (i.e. bin) the skewness values so we can group by them later
    :return:
    """
    skewed_df = pd.read_csv('skewed.csv', sep='\t')
    # 13 bins of 0.1 width
    bins = np.linspace(-0.5, 0.9, 14)

    # There is one fewer label than the number of bins, hence the "1:" slice
    labels = ['%.1f' % elem for elem in bins[1:]]

    print(f"bins: {bins} labels: {labels}")

    # Add the binned column using panda "cut" function
    skewed_df['binned'] = pd.cut(skewed_df['skewness'], bins, labels=labels)
    print(tabulate(skewed_df, headers='keys', tablefmt='psql'))
    dir_path = "/Users/rebjl/PycharmProjects/movie_project/"
    # Save the resulting dataframe as tab separated
    skewed_df.to_csv(dir_path + "skewed.csv", sep="\t")
