from random import randrange

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import glob


def load_data(directory, threshold):
    data = []
    targets = []
    words = []
    for score_path in glob.glob(directory):
        with open(score_path, 'r') as paper_file:
            print(score_path)
            for line in paper_file:
                line = line.split(',')
                target = int(line[-1].strip())
                features = [line[1], line[2], line[3], line[4], line[5], line[6], int(line[6]) - int(line[5])]
                data.append(list(map(lambda x: float(x), features)))
                targets.append(1 if target > threshold else 0)
                words.append(line[0])
    return data, targets, words


class OrdinalClassifier:
    def __init__(self, n_of_classes, classifier):
        self.data = []
        self.targets = []
        self.words = []
        self.training_sets = []
        self.test_sets = []
        self.n_of_classes = n_of_classes
        self.classifier = classifier
        self.clf = [classifier for i in range(1, self.n_of_classes)]
        self.all_data = {}

    def load_all_data(self, directory):
        self.all_data['target_names'] = ["1","2","3","4","5"]
        self.all_data['data'] = []
        self.all_data['target'] = []
        self.all_data['word'] = []
        for score_path in glob.glob(directory):
            with open(score_path, 'r') as paper_file:
                for line in paper_file:
                    line = line.split(',')
                    target = int(line[-1].strip())
                    line[7] = int(line[6]) - int(line[5])
                    self.all_data['data'].append(list(map(lambda x: float(x), line[1:-1])))
                    self.all_data['target'].append(target)
                    self.all_data['word'].append(line[0])

    def get_sets(self, directory):
        for i in range(1, self.n_of_classes):
            data, targets, words = load_data(directory, i)
            self.data.append(data)
            self.targets.append(targets)
            self.words.append(words)
            train, test, train_target, test_target, train_words, test_words = train_test_split(self.data[i-1],
                                                                                               self.targets[i-1],
                                                                                               self.words[i-1],
                                                                                               test_size=0.33,
                                                                                               random_state=42)
            self.training_sets.append({"train": train, "target": train_target, "word": train_words})
            self.test_sets.append({"test": test, "target": test_target, "word": test_words})

    def train(self):
        for i in range(1, self.n_of_classes):
            self.clf[i - 1].fit(self.training_sets[i-1]["train"], self.training_sets[i-1]["target"])
            preds = self.clf[i-1].predict(self.test_sets[i-1]["test"])
            print(accuracy_score(self.test_sets[i-1]["target"], preds))

    def predict_proba(self, values):
        results = []
        results.append([1 - val_probs[1] for val_probs in self.clf[0].predict_proba(values)])
        for i in range(1, self.n_of_classes - 1):
            results.append([x[1] - y[1] for x,y in zip(self.clf[i-1].predict_proba(values),self.clf[i].predict_proba(values))])
        results.append([val_probs[1] for val_probs in self.clf[self.n_of_classes-2].predict_proba(values)])
        # return list(zip(results[0],results[1],results[2],results[3],results[4]))
        return [result.index(max(result)) + 1 for result in list(zip(results[0],results[1],results[2],results[3],results[4]))]


directory = '/home/paula/Descargas/Memoria/extractkeywords/training/*'
classifier = OrdinalClassifier(5, RandomForestClassifier())
classifier.get_sets(directory)
classifier.train()
classifier.load_all_data(directory)
print(list(zip(classifier.predict_proba(classifier.all_data['data']),
               classifier.all_data['target'],
               classifier.all_data['word'])))

# print (list(zip(classifier.clf[1].predict_proba(classifier.all_data['data']),
#            classifier.all_data['target'],
#                 classifier.all_data['word'])))

print(accuracy_score(classifier.all_data['target'], classifier.predict_proba(classifier.all_data['data'])))
