
from dictionary import Dictionary
import numpy as np;
def get_morph_new(MorphUnit, words):
    n_words = len(words);
    if n_words < 2:
        raise ValueError
    gender = np.random.choice(range(4))
    result = [MorphUnit(part="іменник",
                        info={"vidm": 0,
                              'gender': gender}),
              MorphUnit(part="дієслово",
                        info={'gender': gender,
                              "persons": 2,  # np.random.choice(range(3)),
                              "time": np.random.choice(range(3))})]
    np.random.shuffle(result)
    weights = dict(zip(["іменник", "прикметник", "дієслово", "дієприслівник", "прислівник"], [5, 4, 5, 1, 1]))
    while len(result) < n_words:
        weights_result = [weights[x.part] for x in result]
        weights_result = np.array(weights_result)
        weights_result = weights_result / np.ndarray.sum(weights_result)
        index = np.random.choice(range(len(result)), p=weights_result)
        offset = np.random.choice([0])
        result.insert(index + offset, result[index].generate_another())
    return result
