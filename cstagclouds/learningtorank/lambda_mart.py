import pickle
from random import randint

import numpy as np
import pyltr
from sklearn.model_selection import LeaveOneGroupOut, GroupShuffleSplit

from cstagclouds.learningtorank.utils import load_data


def cross_val(data_dir, model_dir, save_model):
    # data_dir = '/home/paula/Descargas/tagclouds-api/cstagclouds/extractkeywords/training/*'
    # model_dir = '/home/paula/Descargas/tagclouds-api/cstagclouds/learningtorank/models/unfiltered/'

    x, y, words, qids, rake, groups = (np.array(l) for l in load_data(data_dir))
    logo = LeaveOneGroupOut()

    for train_index, test_index in logo.split(x, y, groups):
        x_train, x_test = x[train_index], x[test_index]
        y_train, y_test = y[train_index], y[test_index]
        q_train, q_test = qids[train_index], qids[test_index]
        metric = pyltr.metrics.NDCG(len(x_test))
        if save_model:
            model = pyltr.models.LambdaMART(
                metric=metric,
                n_estimators=2000,
                learning_rate=0.03,
                query_subsample=0.5
            )
            model.fit(x_train, y_train, q_train)
            pickle.dump(model,
                        open('%sLambdaMART2/lambdaMART_model_%s.sav' % (model_dir, q_test[0].replace('.txt', '')),
                             'wb'))
        else:
            model = pickle.load(
                open('%sLambdaMART/lambdaMART_model_%s.sav' % (model_dir, q_test[0].replace('.txt', '')), 'rb'))
        pred_test = model.predict(x_test)
        print('%s' % metric.calc_mean(q_test, y_test, pred_test))


def train(data_dir):
    # data_dir = '/home/paula/Descargas/tagclouds-api/cstagclouds/extractkeywords/training/*'

    x, y, words, qids, rake, groups = (np.array(l) for l in load_data(data_dir))
    metric = pyltr.metrics.NDCG(90)

    model = pyltr.models.LambdaMART(
        metric=metric,
        n_estimators=2000,
        learning_rate=0.03,
        max_features=1,
        query_subsample=0.5,
        max_leaf_nodes=10,
        min_samples_leaf=64,
        verbose=1,
    )
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=randint(0,30))
    for train_index, test_index in gss.split(x, y, groups=groups):
        x_train, x_test = x[train_index], x[test_index]
        y_train, y_test = y[train_index], y[test_index]
        q_train, q_test = qids[train_index], qids[test_index]
        w_train, w_test = words[train_index], words[test_index]
        rake_train, rake_test = rake[train_index], rake[test_index]
        model.fit(x_train, y_train, q_train)

        pred_test = model.predict(x_test)
        a = list(zip(q_test, pred_test, w_test))
        a2 = sorted(a, key=lambda x: (x[0], x[1]))
        for word in a2:
            print(word[0], word[1], word[2])
        metric = pyltr.metrics.NDCG(len(x_test))
        print('Random ranking:', metric.calc_mean_random(q_test, y_test))
        print('Our model:', metric.calc_mean(q_test, y_test, pred_test))
        print('Rake:', metric.calc_mean(q_test, y_test, rake_test))


def save(data_dir, model_dir):
    # data_dir = '/home/paula/Descargas/tagclouds-api/cstagclouds/extractkeywords/training/*'
    # model_dir = '/home/paula/Descargas/tagclouds-api/cstagclouds/learningtorank/models/unfiltered/'

    x, y, words, qids, rake, groups = (np.array(l) for l in load_data(data_dir))
    metric = pyltr.metrics.NDCG(90)
    model = pyltr.models.LambdaMART(
        metric=metric,
        n_estimators=2000,
        learning_rate=0.03,
        max_features=1,
        query_subsample=0.5,
        max_leaf_nodes=10,
        min_samples_leaf=64,
        verbose=1,
    )
    model.fit(x, y, qids)
    pickle.dump(model, open("%slambdaMART_model.sav" % model_dir, 'wb'))
